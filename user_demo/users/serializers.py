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

    def create(self, validated_data):

        if not UserVerify.objects.filter(
            phone_number=validated_data.get("phone_number"),
            token=validated_data.get("token"),
            is_verified=True,
        ).exists():
            raise serializers.ValidationError("전화번호 인증이 필요합니다.")

        user = User.objects.create_user(
            email=validated_data.get("email"),
            nickname=validated_data.get("nickname"),
            name=validated_data.get("name"),
            phone_number=validated_data.get("phone_number"),
            password=validated_data.get("password"),
        )

        return user

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


class UserVerifyCreateSerializer(serializers.ModelSerializer):
    phoneNumberRegex = RegexValidator(
        regex=r"^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})$"
    )
    phone_number = serializers.CharField(validators=[phoneNumberRegex])

    def create(self, validated_data):
        validated_data["phone_number"] = validated_data["phone_number"].replace("-", "")
        validated_data["key"] = random.randint(100000, 999999)
        return super().create(validated_data)

    class Meta:
        model = UserVerify
        fields = ["phone_number"]


class UserVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVerify
        fields = ["key", "phone_number", "is_verified", "token"]
        extra_kwargs = {
            "key": {"write_only": True},
            "is_verified": {"read_only": True},
            "token": {"read_only": True},
        }

    def validate(self, data) -> UserVerify:
        phone_number = data.get("phone_number")
        key = data.get("key")

        try:
            verify = (
                UserVerify.objects.filter(
                    phone_number=phone_number,
                    key=key,
                    is_verified=False,
                    created_at__gt=datetime.now()
                    - timedelta(minutes=5),  # 5분 이내 생성된 것만 체크
                )
                .select_for_update()
                .get()
            )
        except UserVerify.DoesNotExist:
            raise serializers.ValidationError("올바른 정보를 입력해주세요.")

        token = str(uuid4()).replace("-", "")

        verify.is_verified = True
        verify.verified_at = datetime.now()
        verify.token = token
        verify.save()

        return verify


class UserLoginSerializer(serializers.Serializer):

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
    email = serializers.EmailField()
    password = serializers.CharField()
    token = serializers.CharField()

    class Meta:
        fields = ["email", "password", "token"]

    def validate(self, data):
        email = data.get("email", None)
        new_password = data.get("password", None)
        token = data.get("token", None)

        user = User.objects.filter(email=email).select_for_update().first()

        verify = (
            UserVerify.objects.filter(
                phone_number=user.phone_number,
                token=token,
                is_verified=True,
            )
            .select_for_update()
            .first()
        )

        if verify is None:
            raise serializers.ValidationError("전화번호 인증이 필요합니다.")

        user.set_password(new_password)
        del new_password
        user.save()

        return user
