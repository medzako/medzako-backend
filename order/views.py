from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from . import models, serializers


class CreateListOrdersView(generics.ListCreateAPIView):
    """Creates and List Orders"""
    permission_classes = [IsAuthenticated]
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer


class RetrieveUpdateOrder(generics.RetrieveUpdateAPIView):
    """Retrieve and Update Order"""
    permission_classes = [IsAuthenticated]
    queryset = models.Order.objects.all()
    serializer_class = serializers.UpdateOrderSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
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
