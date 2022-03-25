"""user_demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView
from users.views import (
    UserView,
    UserMeView,
    UserLoginViews,
    UserFindPasswordViews,
)

from phone_verify.views import UserVerifyCreateViews, UserVerifyConfirmViews

urlpatterns = [
    path("admin", admin.site.urls),
    path("users", UserView.as_view()),
    path("users/me", UserMeView.as_view()),
    path("phone-verify", UserVerifyCreateViews.as_view()),
    path("phone-verify/confirm", UserVerifyConfirmViews.as_view()),
    path("login", UserLoginViews.as_view()),
    path("login/refresh", TokenRefreshView.as_view()),
    path("find-password", UserFindPasswordViews.as_view()),
]
