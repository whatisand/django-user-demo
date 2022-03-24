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
from django.contrib.auth import login, logout

from users.models import User, UserVerify
from users.serializers import (
    UserSerializer,
    UserVerifySerializer,
    UserLoginSerializer,
    UserVerifyCreateSerializer,
    UserFindPasswordSerializer,
)
import utils


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
            created_verify = utils.create_verify(**serializer.validated_data)
            print(created_verify.key)
            return Response(status=201)


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

        try:
            utils.set_password_by_token(**serializer.validated_data)
        except PermissionError:
            return Response(status=403)

        return Response(status=201)
