from django.urls import path
from . import views

app_name = "authentication"

urlpatterns = [
    path("", views.CreateListOrdersView.as_view(), name="create_list_orders"),
    path("<int:pk>/", views.RetrieveUpdateOrder.as_view(), name="retrieve_order")
]
