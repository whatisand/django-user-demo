import random

from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import (
    GenericAPIView,
    CreateAPIView,
    RetrieveDestroyAPIView,
)
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout

from users.models import User, UserVerify


class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):

        if not UserVerify.objects.filter(
            phone_number=validated_data.get("phone_number")
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
        fields = ["id", "email", "name", "nickname", "phone_number", "password"]
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
    key = serializers.IntegerField()

    class Meta:
        fields = ["email", "password", "key"]

    def validate(self, data):
        email = data.get("email", None)
        new_password = data.get("password", None)
        key = data.get("key", None)

        user = User.objects.get(email=email)
        verify = UserVerify.objects.filter(
            phone_number=user.phone_number, key=key
        ).first()

        if verify is None:
            raise serializers.ValidationError("유효하지 않은 요청입니다.")

        user = (
            User.objects.filter(phone_number=verify.phone_number)
            .select_for_update()
            .first()
        )

        user.set_password(new_password)
        del new_password
        user.save()

        return user


class UserViewSet(CreateAPIView, RetrieveDestroyAPIView, GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(data={"message: Login Required"}, status=401)

        user = User.objects.filter(email=request.user.email).get()

        if user is None:
            return Response(data={"message: User not exist"}, status=404)

        return Response(UserSerializer(user).data, status=200)


class UserLoginViews(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request: Request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data
        login(request, user)

        return Response(serializer.data, status=202)


class UserVerifyCreateViews(APIView):
    queryset = UserVerify.objects.all()
    serializer_class = UserVerifyCreateSerializer

    def post(self, request: Request, *args, **kwargs):
        # TODO: 인증 문자 보내는 부분 추가
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            verify = serializer.create(serializer.validated_data)

        return Response(self.serializer_class(verify).data, status=201)


class UserVerifyConfirmViews(APIView):
    serializer_class = UserVerifySerializer

    def post(self, request: Request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)

        # 시리얼라이저에서 요청에 대한 인증 여부 검사, 토큰까지 반환하여 전달
        serializer.is_valid(raise_exception=True)
        # 성공시 성공한 verify 반환
        verify = serializer.validated_data

        return Response(serializer.data, status=201)


class UserFindPasswordViews(APIView):

    serializer_class = UserFindPasswordSerializer

    def post(self, request: Request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data

        return Response(UserSerializer(user).data, status=201)
