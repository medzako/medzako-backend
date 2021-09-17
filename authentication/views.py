from django.http import request
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

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
