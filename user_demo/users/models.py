from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, name, nickname, phone_number, password=None):
        if not phone_number:
            raise ValueError('User must have phone number')
        if not email:
            raise ValueError('User must have user email')
        user = self.model(
            name=name,
            email=self.normalize_email(email),
            nickname=nickname,
            phone_number=phone_number
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, nickname, phone_number, password):
        user = self.create_user(
            name=name,
            email=self.normalize_email(email),
            nickname=nickname,
            phone_number=phone_number,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'phone_number']

    class Meta:
        db_table = "user"
        verbose_name = "유저"


class UserVerify(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    key = models.IntegerField()
    token = models.CharField(max_length=128)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField()

    class Meta:
        db_table = "user_verify"
        verbose_name = "인증"
        verbose_name_plural = "유저 인증"
