from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView, TokenObtainPairView
)
from . import views

app_name = "authentication"

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="get_token"),
    path("refresh/token/", TokenRefreshView.as_view(), name="refresh_token"),
    path("register/", views.RegistrationView.as_view(), name="registration"),
    path("user/", views.FetchUserView.as_view(), name="fetch_user"),
    path("pharmacy/upload-license", views.UploadPharmacyLincenseView.as_view(), name="upload_pharmacy_license"),
    path("rider/upload-license", views.UploadRiderLincenseView.as_view(), name="upload_rider_license"),
]
