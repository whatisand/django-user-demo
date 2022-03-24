import random
from uuid import uuid4

from django.db import transaction

from users.models import User, UserVerify
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


def create_verify(phone_number: str) -> UserVerify:
    # db 형식에 일관적으로 저장하기 위해 하이픈(-) 제거
    phone_number = phone_number.replace("-", "")
    # 6자리 숫자 key 렌덤으로 생성하여 데이터에 저장
    key = random.randint(100000, 999999)

    user_verify = UserVerify(phone_number=phone_number, key=key)
    user_verify.save()

    return user_verify


def is_verified_token(token: str) -> bool:
    is_verified = UserVerify.objects.filter(
        token=token,
        is_verified=True,
    ).exists()

    return is_verified


def get_user_by_token(token: str):
    verify = UserVerify.objects.filter(token=token, is_verified=True).first()
    user = User.objects.filter(phone_number=verify.phone_number).first()

    return user


def create_user_by_validated_data(validated_data):
    ...


def get_user_by_phone_number(phone_number):
    return User.objects.filter(phone_number=phone_number).first()


@transaction.atomic()
def get_verify_token_by_key_phone_number(phone_number: str, key: int):
    """
    전화번호와 key를 이용해 생성된 인증을 컨펌하는 메소드입니다. 인증 성공시 token을 생성하여 저장합니다.

    :param phone_number: 전화번호
    :param key: SMS 발송된 Key
    :return UserVerify: UserVerify 모델 객체
    """
    verify = (
        UserVerify.objects.filter(
            phone_number=phone_number,
            key=key,
            is_verified=False,
            created_at__gt=datetime.now() - timedelta(minutes=5),
        )
        .select_for_update(nowait=True)
        .first()
    )

    if verify is None:
        return None

    token = str(uuid4()).replace("-", "")

    verify.is_verified = True
    verify.verified_at = datetime.now()
    verify.token = token
    verify.save()

    return verify


def set_password_by_token(email, password, token):
    user = User.objects.filter(email=email).first()

    verify = UserVerify.objects.filter(
        phone_number=user.phone_number,
        token=token,
        is_verified=True,
    ).first()

    if verify is None:
        raise PermissionError

    user.set_password(password)
    del password
    user.save()

    return user
