import random
from uuid import uuid4

from django.db import transaction
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from users.models import User
from phone_verify.models import PhoneVerify
from datetime import datetime, timedelta


def send_sms_verify_key(phone_number: str, key: int):
    """
    전화번호와 발급된 key를 이용하여 인증 요청 sms를 발송하는 유틸입니다.

    :param phone_number: 전화번호
    :param key: UserVerify에 발급된 key
    :return: 성공시 True, 실패시 false 반환
    """

    # TODO: SMS 발송 API 콜 하는 부분
    print(f"{phone_number}")
    print(f"[회사명]인증번호를 입력해주세요[{key}]")

    # 성공시 True, 실패시 False 반환
    return True


def create_verify(phone_number: str) -> PhoneVerify:
    # db 형식에 일관적으로 저장하기 위해 하이픈(-) 제거
    phone_number = phone_number.replace("-", "")
    # 6자리 숫자 key 렌덤으로 생성하여 데이터에 저장
    key = random.randint(100000, 999999)

    send_sms_verify_key(phone_number, key)

    user_verify = PhoneVerify(phone_number=phone_number, key=key)
    user_verify.save()

    return user_verify


def is_verified_token(phone_number: str, token: str) -> bool:
    is_verified = PhoneVerify.objects.filter(
        token=token, phone_number=phone_number, is_verified=True, is_used=False
    ).exists()

    return is_verified


def set_used_token(token: str):
    """
    입력받은 전화번호 인증 토큰을 사용한 것으로 체크합니다. 사용 여부와 무관하게 사용한 것으로 체크합니다.
    :param token: 전화번호 인증 후 발급받은 토큰
    :return: 없음
    """
    verify = PhoneVerify.objects.filter(token=token).first()
    verify.is_used = True
    verify.save()


@transaction.atomic()
def get_user_by_token(token: str):
    """
    전화번호 인증받은 토큰으로 가입된 유저가 있으면 해당 유저를 반환합니다.
    반환 후 토큰은 사용된 것으로 체크됩니다.
    :param token: 전화번호 인증 후 발급받은 토큰
    :return: 유저 또는 None(유저 없을시)
    """
    verify = (
        PhoneVerify.objects.filter(token=token, is_verified=True, is_used=False)
        .select_for_update()
        .first()
    )
    user = User.objects.filter(phone_number=verify.phone_number).first()

    # 해당 토큰을 사용한 것으로 간주하여 재사용 불가하게 설정
    verify.is_used = True
    verify.save()

    return user


@transaction.atomic()
def get_verify_token_by_key_phone_number(phone_number: str, key: int):
    """
    전화번호와 key를 이용해 생성된 인증을 컨펌하는 메소드입니다. 인증 성공시 token을 생성하여 저장합니다.
    이미 토큰이 발급된 경우 다시 발급이 불가능합니다.

    :param phone_number: 전화번호
    :param key: SMS 발송된 Key
    :return UserVerify: UserVerify 모델 객체
    """
    verify = (
        PhoneVerify.objects.filter(
            phone_number=phone_number.replace("-", ""),
            key=key,
            is_verified=False,
            created_at__gt=timezone.now() - timedelta(minutes=5),
        )
        .select_for_update()
        .first()
    )

    if verify is None:
        return None

    token = str(uuid4()).replace("-", "")

    verify.is_verified = True
    verify.verified_at = timezone.now()
    verify.token = token
    verify.save()

    return verify


def get_current_user(request):
    authorization_header = request.headers.get("Authorization")
    if not authorization_header:
        return None

    scheme, _, param = authorization_header.partition(" ")

    user_id = AccessToken(param).get("user_id")

    return User.objects.get(id=user_id)


def create_user(validated_data) -> User:

    # TODO: 일부 비즈니스 로직이 모델에 있어서 마음에 들지 않음
    user = User.objects.create_user(
        email=validated_data.get("email"),
        nickname=validated_data.get("nickname"),
        name=validated_data.get("name"),
        phone_number=validated_data.get("phone_number"),
        password=validated_data.get("password"),
    )

    return user


def get_user_by_phone_number(phone_number):
    return User.objects.filter(phone_number=phone_number).first()


def set_password_by_token(email, new_password, token):
    """
    전화번호 인증 후 받은 토큰과 새로운 비밀번호를 입력받아 이메일을 변경합니다.

    :param email: 유저 이메일
    :param new_password: 변경하고자 하는 비밀번호
    :param token: 전화번호 인증 후 발급받은 토큰
    :return:
    """
    user = User.objects.filter(email=email).first()

    if user is None:
        raise LookupError("User Not Found")

    verify = PhoneVerify.objects.filter(
        phone_number=user.phone_number,
        token=token,
        is_verified=True,
        is_used=False,
    ).first()

    if verify is None:
        raise PermissionError("전화번호 인증이 필요합니다.")

    user.set_password(new_password)
    del new_password
    user.save()

    return user


def get_user_by_login_data(data):
    """
    입력받은 정보를 이용해 authenticate를 진행하고 User를 반환합니다.

    :param data: validated data
    :return: User 또는 None
    """
    email = data.get("email", None)
    password = data.get("password", None)
    phone_number = data.get("phone_number", None)
    key = data.get("key", None)

    # TODO: 리펙토링

    # 전화번호와 비밀번호로 로그인 하는 경우, 전화번호로 이메일 찾기
    if email is None and phone_number is not None:
        phone_number = data.get("phone_number").replace("-", "")
        user = get_user_by_phone_number(phone_number)
        email = user.email

    # 이메일, 패스워드 있는 경우 authenticate를 통해 유저 확인
    if email is not None and password is not None:
        user = authenticate(username=email, password=password)
        return user

    # 전화번호와 전화번호 인증 키로 로그인 하는 경우
    if phone_number is not None and key is not None:
        phone_number = data.get("phone_number").replace("-", "")
        verify = get_verify_token_by_key_phone_number(phone_number, key)
        if verify is not None:
            user = get_user_by_token(verify.token)
            return user

    # 이메일과 전화번호 인증 키로 로그인 하는 경우
    if email is not None and key is not None:
        user = User.objects.get(email=email)
        verify = get_verify_token_by_key_phone_number(user.phone_number, key)
        if verify is not None:
            user = get_user_by_token(verify.token)
            return user

    return None
