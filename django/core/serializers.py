from rest_framework import serializers


# Serializa cadastro de usuario.
class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=6)


# Serializa credenciais de login.
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


# Serializa payload vindo do desktop.
class MachineSyncSerializer(serializers.Serializer):
    schema_version = serializers.CharField(required=False, default="1.0", max_length=10)
    machine = serializers.DictField()
    diagnostics = serializers.ListField(child=serializers.CharField(), required=False)
    route = serializers.ListField(child=serializers.DictField(), required=False)
    catalog = serializers.ListField(child=serializers.DictField(), required=False)
    source = serializers.CharField(required=False, max_length=50)
