from django.urls import path
from . import views

app_name = "order"

urlpatterns = [
    path("", views.CreateListOrdersView.as_view(), name="create_list_orders"),
    path("<int:pk>/", views.RetrieveUpdateOrder.as_view(), name="retrieve_order"),
    path("locations/", views.CreateListLocationsView.as_view(), name="create_location"),
    path("locations/<int:pk>/", views.RetrieveUpdateLocation.as_view(), name="retrieve_update_location"),
    path("image/", views.UploadimageView.as_view(), name="upload_image"),
]
