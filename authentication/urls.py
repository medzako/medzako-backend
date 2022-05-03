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
    path("rider-profile/", views.FetchUpdateRiderProfileView.as_view(), name="fetch_update_rider_profile"),
    path("pharmacy/upload-license/", views.UploadPharmacyLincenseView.as_view(), name="upload_pharmacy_license"),
    path("riders/upload-license/", views.UploadRiderLincenseView.as_view(), name="upload_rider_license"),
    # path("rider/update-location/", views.upd.as_view(), name="upload_rider_license"),
    path("users/<int:pk>/", views.UpdateUser.as_view(), name="update_user"),
    path("users/update/", views.UpdateUserNoId.as_view(), name="update_user_no_id"),
    path("pharmacies/<int:pharmacy_id>/licenses/", views.FetchPharmacyLincensesView.as_view(), name="fetch_pharmacy_licenses"),
    path("verify/<slug:token>/", views.verify_user, name="verify_user"),
    path("riders/licenses/", views.FetchRiderLincensesView.as_view(), name="fetch_rider_licenses"),
    path("riders/profile-pic/", views.UploadProfilePicView.as_view(), name="upload_profile_pic"),
    path("send-test-notification/", views.SendNotification.as_view(), name="send_fcm_notification"),
    path("send-fcm-test-data/", views.SendFCMData.as_view(), name="send_fcm_data"),
    path("update-rider-location/", views.CurrentRiderLocationView.as_view(), name="update_rider_location"),

]
