from django.core.validators import RegexValidator
from rest_framework import serializers

from phone_verify.models import PhoneVerify


class PhoneVerifyCreateSerializer(serializers.ModelSerializer):
    # 전화번호 형식 벨리데이터
    phoneNumberRegex = RegexValidator(
        regex=r"^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})$"
    )
    phone_number = serializers.CharField(validators=[phoneNumberRegex])

    class Meta:
        model = PhoneVerify
        fields = ["phone_number"]


class PhoneVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneVerify
        fields = ["key", "phone_number", "is_verified", "token"]
        extra_kwargs = {
            "key": {"write_only": True},  # 반환값에서 key는 반환하지 않도록 설정
            "is_verified": {"read_only": True},
            "token": {"read_only": True},
        }
