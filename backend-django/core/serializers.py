from django.contrib.auth.models import User
from rest_framework import serializers

from .models import MachineSnapshot


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class MachineSyncSerializer(serializers.Serializer):
    schema_version = serializers.CharField(required=False, default="1.0", max_length=10)
    machine = serializers.DictField()
    diagnostics = serializers.ListField(child=serializers.CharField(), required=False)
    route = serializers.ListField(child=serializers.DictField(), required=False)
    catalog = serializers.ListField(child=serializers.DictField(), required=False)
    source = serializers.CharField(required=False, max_length=50)


class MachineSnapshotSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = MachineSnapshot
        fields = [
            "username",
            "schema_version",
            "machine",
            "diagnostics",
            "route",
            "catalog",
            "source",
            "collected_at",
        ]
