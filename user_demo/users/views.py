import random

from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView, CreateAPIView, RetrieveDestroyAPIView
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout

from users.models import User, UserVerify


class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):

        if not UserVerify.objects.filter(phone_number=validated_data.get("phone_number")).exists():
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
    phoneNumberRegex = RegexValidator(regex=r"^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})$")
    phone_number = serializers.CharField(validators=[phoneNumberRegex])

    def create(self, validated_data):
        validated_data["phone_number"] = validated_data["phone_number"].replace("-","")
        validated_data["key"] = random.randint(100000, 999999)
        return super().create(validated_data)

    class Meta:
        model = UserVerify
        fields = ["phone_number"]

# Create your views here.
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
