from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import AdminProfileView, LoginView, UserAPIView

urlpatterns = [
    path("auth/login/",LoginView.as_view(),name="login",),
    # path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/profile/", AdminProfileView.as_view(), name="admin-profile"),
    path("users/", UserAPIView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserAPIView.as_view(), name="user-detail"),
]
