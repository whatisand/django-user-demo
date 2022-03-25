from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from users.serializers import (
    UserSerializer,
    UserLoginSerializer,
    UserFindPasswordSerializer,
)
import services


class UserView(APIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not services.is_verified_token(
            phone_number=serializer.validated_data.get("phone_number"),
            token=serializer.validated_data.get("token"),
        ):
            # 입력받은 전화번호 인증 토큰이 유효하지 않은 경우
            return Response(data={"detail": "전화번호 인증이 필요합니다."}, status=401)

        # 토큰이 유효하면 유저 생성 진행
        user = services.create_user(serializer.validated_data)

        return Response(UserSerializer(user).data, status=201)


class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args, **kwargs):

        user = services.get_current_user(request)

        if user is None:
            return Response(data={"detail": "로그인이 필요합니다."}, status=403)

        return Response(UserSerializer(user).data, status=200)


class UserLoginViews(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request: Request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = services.get_user_by_login_data(serializer.validated_data)

        if user is None:
            return Response(data={"detail": "User not exist"}, status=401)

        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)
        # login(request, user)

        data = {"access_token": str(access_token), "refresh_token": str(refresh_token)}

        return Response(data=data, status=202)


class UserFindPasswordViews(APIView):
    serializer_class = UserFindPasswordSerializer

    def post(self, request: Request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            services.set_password_by_token(
                email=serializer.validated_data.get("email"),
                new_password=serializer.validated_data.get("password"),
                token=serializer.validated_data.get("token"),
            )
        except PermissionError:
            return Response(data={"detail": "전화번호 인증이 필요합니다."}, status=401)
        except LookupError:
            return Response(data={"detail": "전화번호 인증이 필요합니다."}, status=401)

        return Response(status=201)
