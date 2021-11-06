from django.urls import path
from . import views

app_name = "medication"

urlpatterns = [
    path("", views.CreateListMedicationView.as_view(), name="medications"),
    path("categories/", views.CreateListCategoriesView.as_view(), name="categories"),
    path("pharmacies/", views.CreatePharmacyView.as_view(), name="pharmacies"),
    path("<int:pk>/", views.RetrieveUpdateDestroyMedicationView.as_view(), name="update_medications"),
    path("pharmacies/<int:pk>/", views.RetrieveUpdateDestroyPharmacyView.as_view(), name="update_pharmacy"),
    path("categories/<int:pk>/", views.RetrieveUpdateDestroyCategoryView.as_view(), name="update_category"),
    path("pharmacies/rate/", views.RatePharmacyView.as_view(), name="rate_pharmacy"),
    path("search/", views.SearchMedication.as_view(), name="search_medication"),
]
