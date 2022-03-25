from django.core.validators import RegexValidator
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    # 전화번호 인증 후 발급받은 토큰
    token = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "nickname",
            "phone_number",
            "password",
            "token",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "name", "nickname", "phone_number"]


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    key = serializers.IntegerField(required=False, write_only=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        fields = ["email", "password", "phone_number", "key"]


class UserFindPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    class Meta:
        fields = ["email", "password", "token"]
