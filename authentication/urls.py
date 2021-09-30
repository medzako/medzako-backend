from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from . import views

app_name = "authentication"

urlpatterns = [
    path("login/", views.TokenUserDataObtainPairView.as_view(), name="get_token"),
    path("refresh/token/", TokenRefreshView.as_view(), name="refresh_token"),
    path("register/", views.RegistrationView.as_view(), name="registration")
]
