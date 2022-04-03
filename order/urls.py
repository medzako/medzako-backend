from django.urls import path
from . import views

app_name = "order"

urlpatterns = [
    path("", views.CreateListOrdersView.as_view(), name="create_list_orders"),
    path("<int:pk>/", views.RetrieveUpdateOrder.as_view(), name="retrieve_order"),
    path("locations/", views.CreateListLocationsView.as_view(), name="create_location"),
    path("locations/<int:pk>/", views.RetrieveUpdateLocation.as_view(), name="retrieve_update_location"),
    path("image/", views.UploadimageView.as_view(), name="upload_image"),
    path("image/<int:pk>/", views.DeleteimageView.as_view(), name="delete_image"),
    path("payment-webhook/", views.PaymentView.as_view(), name="payment_webhook"),
    path("earnings/", views.FetchEarningsView.as_view(), name="fetch_earnings"),
    path("rider-response/<int:pk>/", views.UpdateRiderHistory.as_view(), name="respond_to_rider_order"),
]
