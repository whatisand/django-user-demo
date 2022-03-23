from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, name, nickname, phone_number, password=None):
        if not phone_number:
            raise ValueError("User must have phone number")
        if not email:
            raise ValueError("User must have user email")

        user = self.model(
            name=name,
            email=self.normalize_email(email),
            nickname=nickname,
            phone_number=phone_number.replace("-", ""),
        )
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, password, name=None, nickname=None):
        user = self.create_user(
            name=name,
            email=self.normalize_email(email),
            nickname=nickname,
            phone_number=phone_number,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    phoneNumberRegex = RegexValidator(
        regex=r"^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})"
    )

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True)
    nickname = models.CharField(max_length=255, null=True)
    phone_number = models.CharField(
        max_length=20, unique=True, validators=[phoneNumberRegex]
    )
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number"]

    class Meta:
        db_table = "user"
        verbose_name = "유저"


class UserVerify(models.Model):
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
        db_table = "user_verify"
        verbose_name = "인증"
        verbose_name_plural = "유저 인증"
