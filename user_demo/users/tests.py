from django.test import TestCase

from users.models import User, UserVerify
# Create your tests here.


class UsersTestCase(TestCase):

    def test_인증되지_않은_전화번호로_회원가입을_요청한다(self):
        res = self.client.post(
                path="/users",
                data={
                    "email": "test@test.in",
                    "password": "testtest",
                    "check_password": "testtest",
                    "nickname": "test",
                    "name": "test",
                    "phone_number": "010-1234-1234",
                    },
                content_type="application/json",
            )

        self.assertEqual(res.status_code, 400)
        data = res.json()

    def test_전화번호_인증을_요청한다(self):
        phone_number = "010-4622-2847"
        res = self.client.post(
            path="/users/verify",
            data={
                "phone_number": phone_number,
            },
            content_type="application/json",
        )

        self.assertEqual(res.status_code, 201)
        verify = UserVerify.objects.filter(phone_number=phone_number).order_by("created_at").first()
        return verify

    def test_질못된_전화번호_형식으로_전화번호_인증을_요청한다(self):
        res = self.client.post(
            path="/users/verify",
            data={
                "phone_number": "000",
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_잘못된_인증_번호로_전화번호_인증을_시도한다(self):
        res = self.client.post(
            path="/users/verify",
            data={
                "phone_number": "010-4622-2847",
                "key": "123123"
            },
            content_type="application/json",
        )

        self.assertEqual(res.status_code, 401)

    def test_유효한_인증_번호로_전화번호_인증을_시도한다(self):
        verify = self.test_전화번호_인증을_요청한다()
        res = self.client.post(
            path="/users/verify/confirm",
            data={
                "phone_number": verify.phone_number,
                "key": verify.key,
            },
            content_type="application/json",
        )

        self.assertEqual(res.status_code, 200)

        return verify

    def test_인증된_전화번호로_회원가입을_한다(self):
        verify = self.test_유효한_인증_번호로_전화번호_인증을_시도한다()

        res = self.client.post(
            path="/users",
            data={
                "email": "andy@gggg.com",
                "password": "123123",
                "check_password": "123123",
                "nickname": "test_nickname",
                "name": "test_name",
                "phone_number": verify.phone_number,
            },
            content_type="application/json",
        )

        self.assertEqual(res.status_code, 201)
        data = res.json()

        user = User.objects.get(email=data['email'])

        return user

    def test_잘못된_정보로_로그인을_한다(self):
        user = self.test_인증된_전화번호로_회원가입을_한다()
        res = self.client.post(
            path="/users/login",
            data={
                "email": user.email,
                "password": "fail",
            },
            content_type="application/json",
        )

        self.assertEqual(res.status_code, 401)

    def test_잘못된_정보로_로그인을_한다(self):
        res = self.client.post(
            path="/users/login",
            data={
                "email": "andy@gggg.com",
                "password": "fail",
            },
            content_type="application/json",
        )

        self.assertEqual(res.status_code, 401)

    def test_가입한_정보로_로그인을_한다(self):
        user = self.test_인증된_전화번호로_회원가입을_한다()
        res = self.client.post(
            path="/users/login",
            data={
                "email": user.email,
                "password": "123123",
            },
            content_type="application/json",
        )

        self.assertEqual(res.status_code, 200)
        return_user = User.objects.get(email=user.email)
        return return_user

