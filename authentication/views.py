from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from rest_framework_simplejwt.views import TokenViewBase

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

    def get(self, request, *args, **kwargs):
        serializer = serializers.RegistrationSerializer(instance=request.user)
        return Response(serializer.data)


class UploadPharmacyLincenseView(generics.CreateAPIView):
    """Upload Pharmacy License"""
    permission_classes = [IsAuthenticated]
    queryset = models.PharmacyLicense.objects.all()


class UploadRiderLincenseView(generics.CreateAPIView):
    """Upload Rider License"""
    permission_classes = [IsAuthenticated]
    queryset = models.RiderLicense.objects.all()

