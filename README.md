# django-user-demo


# Backend Requirements

- Docker
- Docker Compose

# 로컬 실행 방법

- 프로젝트 클론
- docker-compose build
- docker-compose up -d

# 사용 기술

- Python3
- Django, Django Rest Framework
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
    - tests: 유저 관련 테스트코드


# API Endpoint

root: /api/v1

## /users
### GET: 접속한 유저 정보 반환 
`로그인 필요`
                
Response

``` json
{
    "id": 1,
    "email": "andandend2847@gmail.com",
    "name": "김동우",
    "nickname": "test",
    "phone_number": "01046222847"
}
```
        
### POST: 회원가입
`전화번호 인증 토큰 필요`        

Request Body 

```json
{
    "email": "",  // 필수
    "name": "",  
    "nickname": "",
    "phone_number": "",  // 필수
    "password": "",  // 필수
    "token": ""  // 필수
}
```

Response

```json

```
        
## /users/me

### GET: 접속한 유저 정보 반환? 해당 유저 정보 반환?

Request

```json

```

Response

```json

```

### PATCH: 해당 유저의 정보 수정

Request

```json

```

Response

```json

```

### DELETE: 해당 유저 삭제

Request

```json

```

Response

```json

```
        
## /users/find-password

### POST: 비밀번호 찾기(변경) 요청 
`전화번호 인증 토큰 필요`

Request

```json
{
    "email": "user@example.com", // 필수
    "password": "string", // 필수
    "token": "string" // 필수
}
```

Response

```json

```
        
## /users/verify
### POST: 전화번호 인증 요청

Request

```json
{
    "phone_number": "01012345678"  // 필수
}
```

Response

```json
{
    "phone_number": "01012345678"
}
```
        
## /users/verify/confirm
### POST: 전화번호 인증 번호 확인
        
Request Body

```json
{
    "phone_number": "01012341234",  // 필수
    "key": "123654"  // 필수
}
```

Response

```json
{
    "phone_number": "01046222847",
    "is_verified": true,
    "token": "86cf8afb5b6e4f5abbab5b8bfac15acd"
}
```
        
## /users/login

### POST: 로그인

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
        
``` json
    {
        
    }
```
        

# DB
- **user**
    - email
        - unique, PK
    - password
        - 암호화
    - nickname
    - name
    - phone_number
        - 필수
        - unique
    - created_at
    - is_active
    - is_verified
- **user_verify**
    - id
    - phone_number
    - key
    - end_at
    - verified
    - created_at

# 도메인
## 유저
- 식별 가능한 정보로 회원가입 할 수 있다
    - 회원가입시 전화번호 인증을 해야 한다
    - 필수 정보 / 선택 정보 나누기
    - 유저 정보를 수정할 수 있다
        - 유저 정보 수정할 때 받을 인증?
- 로그인된 본인의 정보를 볼 수 있다.
    - 어디까지 보여줄까?
- 특정 유저를 삭제할 수 있다.
- 유저 정보를 수정할 수 있다.

## 전화번호 인증



# 정책
## 전화번호 인증 정책

- 인증 생성 후 5분 이후 토큰 발급 불가
- 토큰 발급후 10분 이후 사용 불가
- 토큰은 1회 발급됨
- 토큰 재사용 불가
