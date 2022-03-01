from django.conf import settings
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from jwt import DecodeError, decode


from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from rest_framework_simplejwt.views import TokenViewBase

from core.permissions import IsCurrentUser, IsRider
from medication.models import Pharmacy
from core.utils.helpers import generate_token, raise_validation_error

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
    permission_classes = []
    queryset = models.PharmacyLicense.objects.all()
    serializer_class = serializers.PharmacyLicenseSerializer


class FetchPharmacyLincensesView(generics.GenericAPIView):
    """Upload Pharmacy License"""
    permission_classes = []
    queryset = models.PharmacyLicense.objects.all()
    serializer_class = serializers.PharmacyLicenseSerializer

    def get(self, request, *args, **kwargs):
        data = {}
        pharmacy_id = kwargs.get('pharmacy_id')
        pharmacy = get_object_or_404(Pharmacy, pk=pharmacy_id)
        serializer = self.get_serializer(pharmacy.licenses.all(), many=True)
        for license in serializer.data:
            data[license['name']] = license
        return Response(data)
        
        
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


class UpdateUser(generics.UpdateAPIView):
    """Update user that uses url params to get user"""
    permission_classes = [IsAuthenticated, IsCurrentUser]
    queryset = models.User.objects.all()
    serializer_class = serializers.UpdateUserSerializer


class UpdateUserNoId(generics.UpdateAPIView):
    """Update user that picks user from request"""
    permission_classes = [IsAuthenticated]
    queryset = models.User.objects.all()
    serializer_class = serializers.UpdateUserSerializer


    def get_object(self):
        return self.request.user


def verify_user(request, token):

    # try:
    #     uid = force_text(urlsafe_base64_decode(uidb64))

    #     user = models.User.objects.get(pk=uid)

    # except Exception as e:
    #     user = None
  
    # if user and generate_token.check_token(user, token):
    #     user.is_email_verified = True
    #     user.save()


    try:
            payload = decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except DecodeError:
        return render(request, 'authentication/activate-failed.html')

    user = get_object_or_404(models.User, email=payload["email"])
    user.is_email_verified = True
    user.save()

    return render(request, 'authentication/activate-failed.html', {"user": user})

