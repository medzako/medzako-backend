from django.db.models.query import QuerySet
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


from core.permissions import IsCustomer, IsRider, IsRiderOwnerObject
from core.utils.constants import DELIVERED, PHARMACIST, RIDER
from core.utils.helpers import raise_validation_error, sendFCMMessage

from . import models, serializers


class CreateListOrdersView(generics.ListCreateAPIView):
    """Creates and List Orders. Use ?status=<status> or is_complete=<boolean> to filter the orders"""
    permission_clasPses = [IsAuthenticated]
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer
    filterset_fields = ('status', 'is_completed')

    def get_queryset(self):
        queryset = QuerySet()
        if self.request.user.user_type == PHARMACIST:
            pharmacy = self.request.user.pharmacist_profile.pharmacy
            if not pharmacy:
                raise_validation_error({'detail': 'This user has no pharmacy attached'})
            queryset = pharmacy.orders.all()

        elif self.request.user.user_type == RIDER:
            queryset = self.request.user.rider_orders.all()

        else:
            queryset = self.request.user.orders.all()
        
        return queryset.order_by('-id')

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        if self.request.method == 'GET':
            serializer = serializers.FetchOrderSerializer(*args, **kwargs)
        return serializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RetrieveUpdateOrder(generics.RetrieveUpdateAPIView):
    """Retrieve and Update Order"""
    permission_classes = [IsAuthenticated]
    queryset = models.Order.objects.all()
    serializer_class = serializers.UpdateOrderSerializer

    def get_queryset(self):
        if self.request.user.user_type == PHARMACIST:
            pharmacy = self.request.user.pharmacist_profile.pharmacy
            if not pharmacy:
                raise_validation_error({'detail': 'This user has no pharmacy attached'})
            return pharmacy.orders.all()
        
        if self.request.user.user_type == RIDER:
            return self.request.user.rider_orders.all()
            
        return self.request.user.orders.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = serializers.RetrieveOrderSerializer(instance)
        data = serializer.data
        items_serializer = serializers.FetchItemsSerializer(instance.items.all(), many=True)
        data['items'] =  items_serializer.data
        data['tracking_id'] = instance.tracking_object.tracking_id
        return Response(data=data)

    
class CreateListLocationsView(generics.ListCreateAPIView):
    """Creates and List Locations"""
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.LocationSerializer

    def get_queryset(self):
        return self.request.user.locations.all()


class RetrieveUpdateLocation(generics.RetrieveUpdateAPIView):
    """Retrieve and Update Location"""
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.LocationSerializer
    queryset = models.Location.objects.all()

    def get_queryset(self):
        queryset = QuerySet()
        if not self.request.user.is_anonymous:
            queryset = self.request.user.locations.all()
        return queryset


class UploadimageView(generics.CreateAPIView):
    """Uploads Image"""
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ImageUploadSerializer
    queryset = models.Image.objects.all()


class DeleteimageView(generics.DestroyAPIView):
    """Delete Image"""
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ImageUploadSerializer
    queryset = models.Image.objects.all()


class FetchEarningsView(generics.GenericAPIView):
    """Fetch user earnings"""

    permission_classes = [IsAuthenticated]
    queryset = QuerySet()
    serializer_class = serializers.PharmacyEarningsSerializer

    def get(self, request, *args, **kwargs):
        queryset = super().get_queryset()
        if request.user.user_type == RIDER:
            queryset = request.user.rider_earnings
            serializer = serializers.RiderEarningsSerializer(queryset, many=True)
        elif request.user.user_type == PHARMACIST:
            if request.user.pharmacist_profile.pharmacy:
                queryset = request.user.pharmacist_profile.pharmacy.pharmacy_earnings
            else:
                raise_validation_error({'detail': 'Create pharmacy first'})
            serializer = serializers.PharmacyEarningsSerializer(queryset, many=True)
        else:
            raise_validation_error({'detail': 'Your user type does not have earnings'})
        return Response(serializer.data)


class UpdateRiderHistory(generics.RetrieveUpdateAPIView):
    """Accept or reject orders"""
    permission_classes = [IsRider, IsRiderOwnerObject]
    queryset = QuerySet()
    serializer_class = serializers.RiderHistorySerializer

    def get_queryset(self):
        return self.request.user.riders_history.all()


class FetchRiderHistory(generics.ListCreateAPIView):
    """View rider history and pending rider orders. use ?filter='all' or =pending, ='accepted', ='rejected'"""
    permission_classes = [IsRider]
    queryset = models.RiderHistory.objects.all()
    serializer_class = serializers.RetrieveRiderHistorySerializer

    def get_queryset(self):
        filter_query = self.request.query_params.get('filter', 'all')

        queryset = super().get_queryset()
        queryset = self.request.user.riders_history.all()
        if filter_query == 'pending':
            queryset = queryset.filter(is_accepted=None)

        elif filter_query == 'accepted':
            queryset = queryset.filter(is_accepted=True)

        elif filter_query == 'rejected':
            queryset = queryset.filter(is_accepted=False)
        
        return queryset


@method_decorator(csrf_exempt, name='dispatch')
class PaymentView(generics.ListCreateAPIView):
    """Payment Web hook"""

    permission_classes = []
    serializer_class = serializers.PaymentSerializer

    def create(self, request, *args, **kwargs):
        try:
            super().create(request, *args, **kwargs)
        except AssertionError as e:
            print(e)
            pass
        
        return Response({})
    

def payment_message(request):

    return render(request, 'order/payment_message.html')


class RateRiderView(generics.UpdateAPIView):
    """Rate Rider"""
    permission_classes = [IsAuthenticated, IsCustomer]
    queryset = models.Order.objects.all()
    serializer_class = serializers.RiderRatesSerializer

    def get_queryset(self):
        return self.request.user.orders.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != DELIVERED:
            raise_validation_error({'detail': 'The order has to be delivered before it can be rated'})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rating = models.RiderRating.objects.create(rider=instance.rider, order=instance, customer=instance.customer,  **serializer.data)
        serializer = self.get_serializer(rating)
        return Response(serializer.data)


class RatePharmacyView(generics.UpdateAPIView):
    """Rate Rider"""
    permission_classes = [IsAuthenticated, IsCustomer]
    queryset = models.Order.objects.all()
    serializer_class = serializers.PharmacyRatesSerializer

    def get_queryset(self):
        return self.request.user.orders.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != DELIVERED:
            raise_validation_error({'detail': 'The order has to be delivered before it can be rated'})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rating = models.PharmacyRating.objects.create(pharmacy=instance.pharmacy, order=instance, customer=instance.customer,  **serializer.data)
        serializer = self.get_serializer(rating)
        return Response(serializer.data)
 