from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from phone_verify.serializers import (
    UserVerifySerializer,
    UserVerifyCreateSerializer,
)
import utils


class UserVerifyCreateViews(APIView):
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
            return Response(data={"detail": "유효하지 않은 인증번호입니다."}, status=401)

        return Response(UserVerifySerializer(confirmed_verify).data, status=200)
