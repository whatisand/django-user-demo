from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from phone_verify.serializers import (
    PhoneVerifySerializer,
    PhoneVerifyCreateSerializer,
)
import services


class PhoneVerifyCreateViews(APIView):
    serializer_class = PhoneVerifyCreateSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            created_verify = services.create_verify(
                phone_number=serializer.validated_data.get("phone_number")
            )
            print(created_verify.key)
            return Response(status=201)


class PhoneVerifyConfirmViews(APIView):
    serializer_class = PhoneVerifySerializer

    def post(self, request: Request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 성공시 성공한 verify 반환
        confirmed_verify = services.get_verify_token_by_key_phone_number(
            **serializer.validated_data
        )

        if confirmed_verify is None:
            return Response(data={"detail": "유효하지 않은 인증번호입니다."}, status=401)

        return Response(PhoneVerifySerializer(confirmed_verify).data, status=200)
