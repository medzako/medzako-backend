from django.db.models.query import QuerySet
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from rest_framework_simplejwt.views import TokenViewBase

from core.permissions import IsRider

from . import serializers
from . import models

class RegistrationView(generics.CreateAPIView):
    """
    Register user with full name, phone number, password, and email
    """

    serializer_class = serializers.RegistrationSerializer
    queryset = models.User.objects.all()
    permission_classes = []

class TokenUserDataObtainPairView(TokenViewBase):
    serializer_class = serializers.ReturnUserInformationLoginSerializer


class FetchUserView(generics.GenericAPIView):
    """Fetch user data"""

    permission_classes = [IsAuthenticated]
    queryset = QuerySet()
    serializer_class = serializers.RegistrationSerializer

    def get(self, request, *args, **kwargs):
        serializer = serializers.RegistrationSerializer(instance=request.user)
        return Response(serializer.data)


class UploadPharmacyLincenseView(generics.CreateAPIView):
    """Upload Pharmacy License"""
    permission_classes = [IsAuthenticated]
    queryset = models.PharmacyLicense.objects.all()
    serializer_class = serializers.PharmacyLicenseSerializer


class UploadRiderLincenseView(generics.CreateAPIView):
    """Upload Rider License"""
    permission_classes = [IsAuthenticated]
    queryset = models.RiderLicense.objects.all()
    serializer_class = serializers.RiderLicenseSerializer


class CurrentRiderLocationView(generics.GenericAPIView):
    """Update rider location"""
    permission_classes = [IsRider]
    serializer_class = serializers.RiderLocationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        data = self.get_serializer(instance=instance).data
        return Response(data=data)
