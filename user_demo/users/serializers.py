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
    """
    (이메일, 전화번호)중 하나와 (비밀번호, 전화번호 인증 키)중 하나를 이용해 로그인이 가능한지 확인합니다.
    로그인이 가능하면 user를 반환합니다.
    """

    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    key = serializers.IntegerField(required=False, write_only=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        fields = ["email", "password", "phone_number", "key"]


class UserFindPasswordSerializer(serializers.Serializer):
    """
    이메일, 변경하고자 하는 비밀번호, 전화번호 인증 토큰을 요청받아,
    토큰이 유효하면 해당 유저의 비밀번호를 변경하고자 하는 비밀번호로 변경합니다.

    시리얼라이저 validation을 진행하면 모든 로직이 진행되고 user를 반환합니다.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    class Meta:
        fields = ["email", "password", "token"]
