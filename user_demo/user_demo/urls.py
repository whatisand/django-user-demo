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
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import (
    UserViewSet,
    UserMeView,
    UserVerifyCreateViews,
    UserLoginViews,
    UserVerifyConfirmViews,
    UserFindPasswordViews,
)

urlpatterns = [
    path("auth/", include("rest_framework.urls")),
    path("admin", admin.site.urls),
    path("users", UserViewSet.as_view()),
    path("users/me", UserMeView.as_view()),
    #     "get": "retrieve",
    #     "patch": "update",
    #     "delete": "destroy",
    # })),
    path("users/verify", UserVerifyCreateViews.as_view()),
    path("users/verify/confirm", UserVerifyConfirmViews.as_view()),
    path("login", UserLoginViews.as_view()),
    path("login/refresh", TokenRefreshView.as_view()),
    path("find-password", UserFindPasswordViews.as_view()),
]
