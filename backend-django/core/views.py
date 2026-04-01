from django.contrib.auth import authenticate
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MachineSnapshot
from .serializers import (
    LoginSerializer,
    MachineSnapshotSerializer,
    MachineSyncSerializer,
    RegisterSerializer,
)

SUPPORTED_SCHEMA_VERSIONS = {"1.0"}


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user": {
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if not user:
            return Response({"detail": "Credenciais invalidas."}, status=status.HTTP_401_UNAUTHORIZED)

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user": {
                    "username": user.username,
                    "email": user.email,
                },
            }
        )


class AuthMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "user": {
                    "username": request.user.username,
                    "email": request.user.email,
                }
            }
        )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.auth:
            request.auth.delete()
        return Response({"detail": "Logout realizado."}, status=status.HTTP_200_OK)


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

        snapshot, _ = MachineSnapshot.objects.update_or_create(
            user=request.user,
            defaults={
                "schema_version": schema_version,
                "machine": payload["machine"],
                "diagnostics": payload.get("diagnostics", []),
                "route": payload.get("route", []),
                "catalog": payload.get("catalog", []),
                "source": payload.get("source", "desktop-agent"),
            },
        )

        return Response(MachineSnapshotSerializer(snapshot).data, status=status.HTTP_200_OK)


class MachineCurrentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        snapshot = MachineSnapshot.objects.filter(user=request.user).first()
        if not snapshot:
            return Response({"detail": "Nenhum snapshot encontrado para o usuario."}, status=404)
        return Response(
            {
                "schema_version": snapshot.schema_version,
                "machine": snapshot.machine,
                "diagnostics": snapshot.diagnostics,
            }
        )


class UpgradeRouteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        snapshot = MachineSnapshot.objects.filter(user=request.user).first()
        if not snapshot:
            return Response({"route": []}, status=200)
        return Response({"route": snapshot.route})


class RecommendationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        snapshot = MachineSnapshot.objects.filter(user=request.user).first()
        if not snapshot:
            return Response({"catalog": []}, status=200)
        return Response({"catalog": snapshot.catalog})
