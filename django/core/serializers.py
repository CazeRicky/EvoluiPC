import re
from rest_framework import serializers

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        # Validação estrita: rejeita caracteres suspeitos para proteger o banco
        if not re.match(r'^[a-zA-Z0-9_.-]+$', value):
            raise serializers.ValidationError("O nome de usuário contém caracteres inválidos.")
        return value

class MachineSyncSerializer(serializers.Serializer):
    schema_version = serializers.CharField(max_length=10, required=False, default="1.0")
    source = serializers.CharField(max_length=50, required=False, default="desktop-agent")
    
    # Recebe o JSON completo com as peças do PC
    machine = serializers.DictField(required=True)
    
    # Listas opcionais para diagnósticos e rotas de upgrade
    diagnostics = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    route = serializers.ListField(required=False, default=list)
    catalog = serializers.ListField(required=False, default=list)

    def validate_source(self, value):
        # Proteção contra injeção no campo source
        if not re.match(r'^[a-zA-Z0-9_-]+$', value):
            raise serializers.ValidationError("A origem (source) contém caracteres inválidos.")
        return value