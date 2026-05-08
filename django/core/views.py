import logging
from urllib import request
from neo4j.exceptions import Neo4jError
from rest_framework import permissions, status
from rest_framework.response import Response
from .models import MachineSnapshot
from rest_framework.views import APIView
from rest_framework.decorators import api_view
# Importe a função que você acabou de criar no neo4j_store
from .neo4j_store import get_upgrade_recommendation

from .neo4j_identity import (
    authenticate_identity,
    ensure_user_identity,
    revoke_token,
)
from .neo4j_store import (
    assign_random_pc_to_user,
    ensure_user_node,
    get_user_profile,
    get_user_pc_parts,
    get_user_upgrade_options,
    upsert_user_profile,
    upsert_user_pc_parts,
    upsert_user_upgrade_options,
    get_all_cpus,
    get_all_gpus,
    get_gpu_compatibility,
)
from .serializers import (
    MachineSyncSerializer,
    RegisterSerializer,
)

logger = logging.getLogger(__name__)

# Versoes de schema aceitas pela API.
SUPPORTED_SCHEMA_VERSIONS = {"1.0"}


# Endpoint de cadastro.
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            identity = ensure_user_identity(
                username=serializer.validated_data["username"],
                email=serializer.validated_data.get("email", ""),
                password=serializer.validated_data["password"],
            )
            ensure_user_node(identity)
            # assign_random_pc_to_user(identity)
            upsert_user_profile(
                identity,
                {
                    "registration": {
                        "username": identity["username"],
                        "email": identity["email"],
                    },
                    "auth": {
                        "token_issued": True,
                    },
                },
                source="web-register",
                event_type="register",
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except RuntimeError as exc:
            logger.exception("Runtime error no cadastro")
            return Response(
                {"detail": "Falha ao salvar usuario no banco de identidade."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Neo4jError:
            logger.exception("Erro do Neo4j no cadastro")
            return Response(
                {"detail": "Falha ao conectar no banco Neo4j."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as exc:
            logger.exception("Erro inesperado no cadastro")
            return Response(
                {"detail": f"Erro interno no cadastro: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "token": identity["token"],
                "user": {
                    "id": identity["id"],
                    "username": identity["username"],
                    "email": identity["email"],
                },
            },
            status=status.HTTP_201_CREATED,
        )


# Endpoint de login.
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            identity = authenticate_identity(
                username=serializer.validated_data["username"],
                password=serializer.validated_data["password"],
            )
        except Neo4jError:
            logger.exception("Erro do Neo4j no login")
            return Response(
                {"detail": "Falha ao conectar no banco Neo4j."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if not identity:
            return Response(
                {"detail": "Credenciais invalidas."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            upsert_user_profile(
                identity,
                {
                    "auth": {
                        "last_login": True,
                    }
                },
                source="web-login",
                event_type="login",
            )
        except Neo4jError:
            logger.exception("Erro do Neo4j ao atualizar perfil no login")
            return Response(
                {"detail": "Falha ao atualizar dados no banco Neo4j."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {
                "token": identity["token"],
                "user": {
                    "id": identity["id"],
                    "username": identity["username"],
                    "email": identity["email"],
                },
            }
        )


# Endpoint de dados do usuario autenticado.
class AuthMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = get_user_profile(request.user.id)
        return Response(
            {
                "user": {
                    "id": request.user.id,
                    "username": request.user.username,
                    "email": request.user.email,
                },
                "profile": profile["profile"] if profile else {},
                "profile_source": profile["source"] if profile else "neo4j-empty",
            }
        )


# Endpoint de logout por token.
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.auth:
            revoke_token(request.auth)
        return Response(
            {"detail": "Logout realizado."},
            status=status.HTTP_200_OK,
        )


# Endpoint de sincronizacao da maquina.
class MachineSyncView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = MachineSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data
        schema_version = payload.get("schema_version", "1.0")

        if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
            return Response(
                {
                    "detail": "schema_version nao suportada.",
                    "supported_versions": sorted(SUPPORTED_SCHEMA_VERSIONS),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        source = payload.get("source", "desktop-agent")
        pc_data = upsert_user_pc_parts(
            user=request.user,
            machine=payload["machine"],
            diagnostics=payload.get("diagnostics", []),
            source=source,
        )
        upgrade_data = upsert_user_upgrade_options(
            user=request.user,
            route=payload.get("route", []),
            catalog=payload.get("catalog", []),
            source=source,
        )
        upsert_user_profile(
            request.user,
            {
                "machine": payload["machine"],
                "diagnostics": payload.get("diagnostics", []),
                "route": payload.get("route", []),
                "catalog": payload.get("catalog", []),
                "schema_version": schema_version,
                "source": source,
            },
            source=source,
            event_type="machine_sync",
        )

        return Response(
            {
                "user_id": request.user.id,
                "username": request.user.username,
                "schema_version": schema_version,
                "machine": pc_data["machine"],
                "diagnostics": pc_data["diagnostics"],
                "route": upgrade_data["route"],
                "catalog": upgrade_data["catalog"],
                "source": source,
                "collected_at": pc_data["collected_at"],
            },
            status=status.HTTP_200_OK,
        )


# Endpoint do snapshot atual.
class MachineCurrentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = get_user_pc_parts(request.user.id)
        if not data:
            return Response(
                {
                    "user_id": request.user.id,
                    "schema_version": "1.0",
                    "machine": {},
                    "diagnostics": [],
                    "route": [],
                    "catalog": [],
                    "source": "neo4j-empty",
                    "is_new_user": True,
                },
                status=200,
            )

        return Response(
            {
                "user_id": request.user.id,
                "schema_version": "1.0",
                "machine": data["machine"],
                "diagnostics": data["diagnostics"],
                "source": data["source"],
                "collected_at": data["collected_at"],
            },
            status=200,
        )


# Endpoint de rota de upgrade.
class UpgradeRouteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = get_user_upgrade_options(request.user.id)
        if not data:
            return Response(
                {
                    "user_id": request.user.id,
                    "schema_version": "1.0",
                    "route": [],
                    "source": "neo4j-empty",
                    "is_new_user": True,
                },
                status=200,
            )

        return Response(
            {
                "user_id": request.user.id,
                "schema_version": "1.0",
                "route": data["route"],
                "source": data["source"],
            },
            status=200,
        )


# Endpoint de recomendacoes.
class RecommendationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = get_user_upgrade_options(request.user.id)
        if not data:
            return Response(
                {
                    "user_id": request.user.id,
                    "schema_version": "1.0",
                    "catalog": [],
                    "source": "neo4j-empty",
                    "is_new_user": True,
                },
                status=200,
            )

        return Response(
            {
                "user_id": request.user.id,
                "schema_version": "1.0",
                "catalog": data["catalog"],
                "source": data["source"],
            },
            status=200,
        )

@api_view(['GET'])
def upgrade_route_me(request):
    """
    Endpoint para obter upgrade recomendado baseado na máquina do usuário.
    Retorna recomendação de CPU com melhor custo-benefício.
    """
    try:
        # 1. Tenta buscar os dados reais da máquina do usuário no Neo4j
        user_pc_data = get_user_pc_parts(request.user.id)
        
        if user_pc_data and user_pc_data.get("machine"):
            current_mb = user_pc_data["machine"].get("motherboard", "A320M")
            current_score = int(user_pc_data["machine"].get("cpu_score", 4000))
        else:
            # PLANO B: Se o usuário não tiver PC, usa um Setup Virtual!
            current_mb = "A320M"  # Uma placa-mãe básica
            current_score = 4000  # Uma pontuação baixa para forçar um upgrade
            
    except Exception as e:
        # Fallback em caso de erro ao buscar dados do Neo4j
        print(f"⚠️ Usando PC Virtual (Fallback). Motivo: {e}")
        current_mb = "A320M"
        current_score = 4000

    # 2. Chama a Inteligência do Neo4j para recomendação
    try:
        upgrade_data = get_upgrade_recommendation(current_mb, current_score)
    except Exception as e:
        print(f"⚠️ Erro ao buscar recomendação: {e}")
        upgrade_data = []
    
    # 3. Formata a resposta para o frontend
    response_data = []
    if upgrade_data and len(upgrade_data) > 0:
        response_data.append({
            "id": 1,
            "component": "Processador",
            "recommendation": upgrade_data[0].get('recommendation', 'N/A'),
            "reason": "Maior salto de performance pelo menor preço. Totalmente compatível com sua placa-mãe atual, entregando o melhor custo-benefício da geração.",
            "estimatedPrice": upgrade_data[0].get('price', 0)
        })
        
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def list_cpus(request):
    """
    Endpoint para listar todos os processadores disponíveis no banco.
    """
    try:
        cpus = get_all_cpus()
        return Response({
            "status": "success",
            "data": cpus,
            "count": len(cpus)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def list_gpus(request):
    """
    Endpoint para listar todas as GPUs disponíveis no banco.
    """
    try:
        gpus = get_all_gpus()
        return Response({
            "status": "success",
            "data": gpus,
            "count": len(gpus)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def gpu_compatibility(request, gpu_name):
    """
    Endpoint para listar compatibilidades de uma GPU específica.
    """
    try:
        compatibility = get_gpu_compatibility(gpu_name)
        return Response({
            "status": "success",
            "gpu": gpu_name,
            "compatibility": compatibility,
            "count": len(compatibility)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    