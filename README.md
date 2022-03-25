# django-user-demo


# Backend Requirements

- Docker
- Docker Compose

# 실행 방법 (로컬 개발용)

현재 프로덕션 배포 관련 설정이 되어있지 않은 상태입니다. 유의해주세요.
## With Docker
Ubuntu 20.04 기준

- 도커 설치
  ```
  $ sudo apt-get update
 
  $ sudo apt-get -y install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

  $ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

  $  echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

  $  sudo apt-get update
  $ sudo apt-get install docker-ce docker-ce-cli containerd.io
  ```

- 도커 컴포즈 설치
  ```
  $  sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

  $ sudo chmod +x /usr/local/bin/docker-compose
  ```

- 프로젝트 클론 또는 프로젝트 폴더 접근
  ```
  $ git clone https://github.com/whatisand/django-user-demo.git

  $ cd django-user-demo/user_demo
  ```
- 도커 이미지 빌드
  ```
  $ docker-compose build
  ```
- 도커 컴포즈 실행
  ```
  $ docker-compose up -d
  ```

## Without Docker

- python3.8 이상 필요

- 프로젝트 클론 또는 프로젝트 폴더 접근
  ```
  $ git clone https://github.com/whatisand/django-user-demo.git

  $ cd django-user-demo/user_demo
  ```
- 디펜던시 설치
  ```
  $ pip install --upgrade pip
  $ pip install -r requirements.txt
  ```
- 서버 실행
  ```
  $ python3 manage.py runserver 0:8000
  ```

- \+ 테스트 진행
  ```
  $ python3 manage.py test
  ```


# 사용 기술

- Python3
- Django
- Django Rest Framework, Rest Framework Simplejwt
- PostgreSQL
- Docker, Docker Compose

# 프로젝트 구조
- user_demo: 프로젝트 세팅, 라우팅
    - setting
    - urls
- users: 유저 관련 앱
    - models: 유저 모델 정의
    - serializers: 요청, 응답 벨리데이션
    - views: 
    - tests: 유저 관련 테스트 코드


# API Endpoint

root: /api/v1

## /users/verify
### POST: 전화번호 인증번호 전송 요청

Request Body 

```json
{
    "phone_number": "010-1234-1234"  // 필수
}
```

Response
성공시

`201 Created`
```json
No Data
```

## /users/verify/confirm
### POST: 전화번호와 전송된 key로 전화번호 인증 및 전화번호 인증 토큰 발급

Request Body

```json
{
    "phone_number": "010-1234-1234",  // 필수, 문자열
    "key": "000111"  // 필수, 숫자
}
```

Response

성공시

`200 Success`

```json

{
    "phone_number": "01046222847", // 문자열
    "is_verified": true,
    "token": "215c28eeae484eb2b86e134a4fbc66d8" // 회원가입, 비밀번호 찾기 요청시 사용되는 토큰
}
```

실패시

`400 Bad Request`

``` json
{
    "key": [
        "유효한 정수(integer)를 넣어주세요."
    ],
    "phone_number": [
        "이 필드는 blank일 수 없습니다."
    ]
}
```

`401 Unauthorized`

``` json

```

## /users
### POST: 회원가입
`전화번호 인증 토큰 필요`

Request Body 

```json
{
    "email": "example@exam.com",  // 필수
    "name": "이름입니다",  // 선택
    "nickname": "닉네임입니dang",  // 선택
    "phone_number": "010-1234-5678",  // 필수, 전화번호 인증 요청한 전화번호와 동일해야 함
    "password": "",  // 필수
    "token": ""  // 필수 (전화번호 인증 성공후 받은 토큰)
}
```

Response

성공시

`201 Created`

```json
{
    "id": 3,
    "email": "test@test.im",
    "name": "test",
    "nickname": "test1234",
    "phone_number": "01012345678"
}
```

## /users/find-password

### POST: 비밀번호 찾기(변경) 요청 
`전화번호 인증 토큰 필요`

Request

```json
{
    "email": "user@example.com", // 필수
    "password": "string", // 필수
    "token": "string" // 필수 (전화번호 인증 성공 후 받은 토큰)
}
```

Response

성공시

`201 Created`

```json


```

## /login

### POST: 로그인

- 로그인시 이메일 대신 전화번호를 사용할 수 있습니다. 비밀번호 대신 전화번호 인증시 SMS로 받은 key를 입력하여 로그인 할 수 있습니다.
  - user_id 로도 식별은 가능하지만 실제로 사용되지 않을 것으로 생각하여 개발하지 않았습니다.
- token이 아닌 SMS로 발송된 key로 로그인 한다는 점을 유의해주세요.
- 요청시 필드명을 유의해주세요.


Request Body

```json
{
    // 둘 중 하나 선택
    "email": "example@email.com",
    "phone_number": "01012341234",  
        
    // 둘 중 하나 선택
    "password": "string",
    "key": "123654"
}
```

Response
성공시

`202 Accepted`

``` json
{
    "access_token": "string",
    "refresh_token": "string"
}
```


## /login/refresh

### POST: 토큰 리프래시

Request Body

```json
{
    "refresh": "string"
}
```

Response
성공시

`202 Accepted`

``` json
{
    "access": "string"
}
```



## /users/me

### GET: 로그인한 본인 정보 반환

Request

`Bearer 필요`

HEADER 

Authorization: Bearer {access_token}


Response

``` json
{
    "id": 1,
    "email": "andandend2847@gmail.com",
    "name": "김동우",
    "nickname": "test",
    "phone_number": "01012341234"
}
```


# DB
- **user** : 유저 정보
    - email: 이메일
        - unique, PK
    - password: 비밀번호
    - nickname: 유저 닉네임
    - name: 유저 이름
    - phone_number: 전화번호
        - not null
        - unique
    - created_at: 가입 시점
    - is_active: 활성화 여부
- **user_verify** : 유저 전화번호 인증 관련 정보
    - id
    - phone_number: 인증 요청한 전화번호
    - key: 인증 요청시 발급되어 SMS로 전송된 키
    - is_verified: 전화번호와 키로 인증 성공하여 토큰 발급되었는지 검증
    - token: 인증 성공시 발급된 토큰
    - is_used: 토큰 재사용 불가하기 위한 
    - created_at: 


# 도메인
## 유저
- 회원가입
    - 회원가입시 전화번호 인증을 해야 한다
    - 필수 정보 / 선택 정보 나누기
    - 유저 정보를 수정할 수 있다
        - 유저 정보 수정할 때 받을 인증?
- 로그인
  - 식별 가능한 정보로 로그인 가능하다.
    - 이메일, 전화번호 / 비밀번호, 전화번호 인증 키
- 로그인된 본인의 정보를 볼 수 있다.

## 전화번호 인증
- 전화번호로 전화번호 인증 요청을 할 수 있다.
- SMS로 발송된 인증 키와 전화번호로 전화번호 인증을 할 수 있다.
  - 인증 성공시 token 발급


# 정책
## 전화번호 인증 정책

- 인증 생성 후 5분 이후 인증(토큰 발급) 불가
- 토큰 발급후 10분 이후 사용 불가
- 토큰은 1회 발급됨
- 토큰 재사용 불가

## 로그인 토큰 정책

- access token은 5분 후 만료
- refresh token은 1일 후 만료


# 진행해야 하는 것

## 기능
* [ ] 유저 정보 수정
* [ ] 유저 회원탈퇴


## 구조
* [ ] 유저, 전화번호 인증 앱 나누기