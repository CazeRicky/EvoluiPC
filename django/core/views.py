from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

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
)
from .serializers import (
    MachineSyncSerializer,
    RegisterSerializer,
)

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
            assign_random_pc_to_user(identity)
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
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except RuntimeError:
            return Response(
                {"detail": "Falha ao salvar usuario no banco de identidade."},
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
            },
            status=status.HTTP_201_CREATED,
        )


# Endpoint de login.
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identity = authenticate_identity(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if not identity:
            return Response({"detail": "Credenciais invalidas."}, status=status.HTTP_401_UNAUTHORIZED)
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
        return Response({"detail": "Logout realizado."}, status=status.HTTP_200_OK)


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
