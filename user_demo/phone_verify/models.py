from django.db import models
from django.core.validators import RegexValidator


class PhoneVerify(models.Model):
    phoneNumberRegex = RegexValidator(
        regex=r"^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})"
    )

    phone_number = models.CharField(max_length=20, validators=[phoneNumberRegex])
    key = models.IntegerField()  # 전화번호 인증에 필요한 키
    token = models.CharField(max_length=64, null=True)  # 전화번호 인증 성공시 발급받는 토큰
    is_verified = models.BooleanField(default=False)  # 전화번호 인증 성공 여부 (토큰 발급 여부)
    created_at = models.DateTimeField(auto_now_add=True)  # 생성시점 (문자 발송 시점)
    verified_at = models.DateTimeField(null=True)  # 전화번호 인증 성공 시간
    is_used = models.BooleanField(default=False)  # 전화번호 인증 받은 후 발급받은 토큰으로 API 콜 1회만 가능

    class Meta:
        db_table = "phone_verify"
        verbose_name = "인증"
        verbose_name_plural = "유저 인증"
