from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from . import models, serializers
from core.permissions import IsAdminOrReadOnly

RATING = 'rating'
POPULARITY = 'popularity'
DELIVERY_FEE = 'delivery_fee'
DELIVERY_TIME = 'delivery_time'


class CreateListMedicationView(generics.ListCreateAPIView):
    """Creates and List Medications"""

    permission_classes = [IsAdminOrReadOnly]
    queryset = models.Medication.objects.all()
    serializer_class = serializers.MedicationSerializer


class CreateListCategoriesView(generics.ListCreateAPIView):
    """Creates and list Categories"""    

    permission_classes = [IsAdminOrReadOnly]
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer


class CreatePharmacyView(generics.ListCreateAPIView):
    """
    Creates and list Pharmacies
    query parameters:
        - order-by (rating, popularity, delivery_fee, delivery_time)
        - lat
        - long
    """

    permission_classes = [IsAdminOrReadOnly]
    queryset = models.Pharmacy.objects.all()
    serializer_class = serializers.PharmacySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        order_by = self.request.query_params.get('order-by', RATING)
        if order_by == RATING:
            queryset = queryset.order_by('-rating')
        elif order_by == POPULARITY:
            queryset = queryset.order_by('-completed_orders')

        return queryset
            

class RetrieveUpdateDestroyPharmacyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve and update Pharmacy""" 

    permission_classes = [IsAdminOrReadOnly]
    queryset = models.Pharmacy.objects.all()
    serializer_class = serializers.SinglePharmacySerializer


class RetrieveUpdateDestroyMedicationView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete Medication"""

    permission_classes = [IsAdminOrReadOnly]
    queryset = models.Medication.objects.all()
    serializer_class = serializers.MedicationSerializer


class RetrieveUpdateDestroyCategoryView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete Category"""

    permission_classes = [IsAdminOrReadOnly]
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer


class RatePharmacyView(generics.CreateAPIView):
    """Rate Order"""
    permission_classes = [IsAuthenticated]
    queryset = models.Rating.objects.all()
