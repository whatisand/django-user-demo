import random
from datetime import datetime, timedelta
from uuid import uuid4

from django.core.validators import RegexValidator
from django.contrib.auth import authenticate, login, logout
from rest_framework import serializers

from users.models import User, UserVerify


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

    def create(self, validated_data):
        # 입력받은 전화번호와, 발급된 토큰이 일치하는 것이 있는지 확인
        if not UserVerify.objects.filter(
            phone_number=validated_data.get("phone_number"),
            token=validated_data.get("token"),
            is_verified=True,
        ).exists():
            # 일치하는 전화번호 인증이 없으면 에러 반환
            raise serializers.ValidationError("전화번호 인증이 필요합니다.")

        # 일치하는 것이 있으면 유저 생성 진행
        user = User.objects.create_user(
            email=validated_data.get("email"),
            nickname=validated_data.get("nickname"),
            name=validated_data.get("name"),
            phone_number=validated_data.get("phone_number"),
            password=validated_data.get("password"),
        )

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "name", "nickname", "phone_number"]


class UserVerifyCreateSerializer(serializers.ModelSerializer):
    # 전화번호 형식 벨리데이터
    phoneNumberRegex = RegexValidator(
        regex=r"^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})$"
    )
    phone_number = serializers.CharField(validators=[phoneNumberRegex])

    class Meta:
        model = UserVerify
        fields = ["phone_number"]


class UserVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVerify
        fields = ["key", "phone_number", "is_verified", "token"]
        extra_kwargs = {
            "key": {"write_only": True},  # 반환값에서 key는 반환하지 않도록 설정
            "is_verified": {"read_only": True},
            "token": {"read_only": True},
        }


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

    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)
        phone_number = data.get("phone_number", None)
        key = data.get("key", None)

        # TODO: 리펙토링

        if email is None and phone_number is not None:
            phone_number = data.get("phone_number").replace("-", "")
            user = User.objects.filter(phone_number=phone_number).first()
            email = user.email

        if phone_number is not None and key is not None:
            phone_number = data.get("phone_number").replace("-", "")
            verify = UserVerify.objects.filter(
                phone_number=phone_number, key=key
            ).first()
            if verify is not None:
                user = User.objects.filter(phone_number=verify.phone_number).first()
                return user

        if email is not None and key is not None:
            user = User.objects.get(email=email)
            verify = UserVerify.objects.filter(
                phone_number=user.phone_number, key=key
            ).first()
            if verify is not None:
                user = User.objects.filter(phone_number=verify.phone_number).first()
                return user

        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError("유저 정보가 없습니다.")

        return user


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
