from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from users.models import User, UserVerify
from users.serializers import (
    UserSerializer,
    UserVerifySerializer,
    UserLoginSerializer,
    UserVerifyCreateSerializer,
    UserFindPasswordSerializer,
)
import utils


class UserView(APIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not utils.is_verified_token(serializer.validated_data.get("token")):
            # 입력받은 전화번호 인증 토큰이 유효하지 않은 경우
            return Response(status=401)

        # 토큰이 유효하면 유저 생성 진행
        user = utils.create_user(serializer.validated_data)

        return Response(UserSerializer(user).data, status=201)


class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args, **kwargs):

        user = utils.get_current_user(request)

        if user is None:
            return Response(data={"detail": "User not exist"}, status=404)

        return Response(UserSerializer(user).data, status=200)


class UserLoginViews(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request: Request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = utils.get_user_by_login_data(serializer.validated_data)

        if user is None:
            return Response(status=401)

        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)
        # login(request, user)

        data = {"access_token": str(access_token), "refresh_token": str(refresh_token)}

        return Response(data=data, status=202)


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
        serializer.is_valid(raise_exception=True)
        # 성공시 성공한 verify 반환
        confirmed_verify = utils.get_verify_token_by_key_phone_number(
            **serializer.validated_data
        )

        if confirmed_verify is None:
            return Response(UserVerifySerializer(confirmed_verify).data, status=401)

        return Response(UserVerifySerializer(confirmed_verify).data, status=201)


class UserFindPasswordViews(APIView):

    serializer_class = UserFindPasswordSerializer

    def post(self, request: Request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            utils.set_password_by_token(**serializer.validated_data)
        except PermissionError:
            return Response(status=401)
        except LookupError:
            return Response(status=401)

        return Response(status=201)
