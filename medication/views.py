from decimal import Decimal
from django.db.models.aggregates import Count
from geopy import distance

from rest_framework import filters
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Value
from core.utils.helpers import add_distance_to_pharmacy, get_coordinate_distance, raise_validation_error
from . import models, serializers
from core.permissions import IsAdminOrReadOnly

RATING = 'rating'
POPULARITY = 'popularity'
DELIVERY_FEE = 'delivery_fee'
PROXIMITY = 'proximity'
    

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
        - order-by (rating, popularity, delivery_fee, proximity)
        - lat
        - long
    """

    permission_classes = [IsAdminOrReadOnly]
    queryset = models.Pharmacy.objects.all()
    serializer_class = serializers.PharmacySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        order_by = self.request.query_params.get('order-by', PROXIMITY)

        if order_by == RATING:
            queryset = queryset.order_by('-rating')
        elif order_by == POPULARITY:
            queryset = queryset.order_by('-completed_orders')
            
        return queryset

    def list(self, request, *args, **kwargs):
        lat = request.query_params.get('lat')
        long = request.query_params.get('long')
        order_by = self.request.query_params.get('order-by', PROXIMITY)

        try:
            lat = Decimal(lat)
            long = Decimal(long)
        except ValueError:
            return raise_validation_error({'detail': 'Ensure the latitude and the longitude are decimals'})
        
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data.copy()
        data = [add_distance_to_pharmacy(item, (lat, long)) for item in data]
        
        if order_by == PROXIMITY:
            data = sorted(data, key=lambda x: x['distance'], reverse=False)
        return Response(data)


class RetrieveUpdateDestroyPharmacyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve and update Pharmacy""" 

    permission_classes = [IsAdminOrReadOnly]
    queryset = models.Pharmacy.objects.all()
    serializer_class = serializers.SinglePharmacySerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        stock_serializer = serializers.StockSerializer(instance.available_stock, many=True)
        data['stock'] = stock_serializer.data
        return Response(data=data)


class RetrieveUpdateDestroyMedicationView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete Medication"""

    permission_classes = [IsAdminOrReadOnly]
    queryset = models.Medication.objects.all()
    serializer_class = serializers.MedicationSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        stock_serializer = serializers.MedicationStockSerializer(instance.stock, many=True)
        data['stock'] = stock_serializer.data
        return Response(data=data)


class RetrieveUpdateDestroyCategoryView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, and delete Category
    Also fetches medication under this category
    """

    permission_classes = [IsAdminOrReadOnly]
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        medication_serializer = serializers.MedicationSerializer(instance.medications, many=True)
        data['medications'] = medication_serializer.data
        return Response(data=data)


class RatePharmacyView(generics.CreateAPIView):
    """Rate Order"""
    permission_classes = [IsAuthenticated]
    queryset = models.Rating.objects.all()
    serializer_class = serializers.RatesSerializer


class SearchMedication(generics.ListCreateAPIView):
    "Search medication by adding ?search=name parameter to the URL"

    search_fields = ['name', 'scientific_name']
    filter_backends = (filters.SearchFilter,)
    queryset = models.Medication.objects.all()
    serializer_class = serializers.MedicationSerializer
