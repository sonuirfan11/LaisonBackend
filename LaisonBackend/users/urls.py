from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserLoginOTPView,
    UserLoginVerifyView,
    ProfileView,
    UpdateProfileView,
    LogoutView
)

urlpatterns = [
    path("login/otp", UserLoginOTPView.as_view()),
    path("login/verify", UserLoginVerifyView.as_view()),
    path("user/profile", ProfileView.as_view(), name='profile'),
    path("user/profile/update", UpdateProfileView.as_view(), name='profile-update'),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("user/logout", LogoutView.as_view()),
]
