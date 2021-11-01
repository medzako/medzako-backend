from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer

from . import models, serializers


class CreateListOrdersView(generics.ListCreateAPIView):
    """Creates and List Orders"""
    permission_classes = [IsAuthenticated]
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer

    def get_queryset(self):
        return self.request.user.orders.all()

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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = serializers.RetrieveOrderSerializer(instance)
        data = serializer.data
        items_serializer = serializers.FetchItemsSerializer(instance.items.all(), many=True)
        data['items'] =  items_serializer.data
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

    def get_queryset(self):
        return self.request.user.locations.all()


class UploadimageView(generics.CreateAPIView):
    """Uploads Image"""
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ImageUploadSerializer
