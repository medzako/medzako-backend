from django.conf import settings
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from jwt import decode, DecodeError

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.utils.constants import USER_TYPES
from core.utils.helpers import raise_validation_error

from . import models
from core.utils.validators import validate_password


class RegistrationSerializer(serializers.ModelSerializer):

    user_type = serializers.ChoiceField(choices=USER_TYPES)
    password = serializers.CharField(max_length=128, validators=[validate_password], write_only=True)

    def create(self, validated_data):
        try:
            user = models.User.objects.create_user(**validated_data)
        except ValidationError as e:
            pass
        user.save()
        return user


    class Meta:
        model = models.User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only':True},
            'last_login': {'write_only':True},
            'groups': {'write_only':True},
            'user_permissions': {'write_only':True}
        }


class ReturnUserInformationLoginSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['first_name'] = user.first_name
        token['second_name'] = user.second_name
        token['is_admin'] = user.is_admin
        token['is_superuser'] = user.is_superuser
        return token

class PharmacyLicenseSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        name = validated_data.get('name')
        licenses = models.PharmacyLicense.objects.filter(name=name)
        for license in licenses:
            license.delete()
        return super().create(validated_data)
        
    class Meta:
        model = models.PharmacyLicense
        fields = '__all__'


class RiderLicenseSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        name = validated_data.get('name')
        licenses = models.RiderLicense.objects.filter(name=name)
        for license in licenses:
            license.delete()

        validated_data['rider_profile'] = self.context['request'].user.rider_profile
        return super().create(validated_data)

    class Meta:
        model = models.RiderLicense
        fields = '__all__'



class RiderProfileImageSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        profile = self.context['request'].user.rider_profile

        try:
            profile.profile_pic.delete()
        except models.RiderProfile.profile_pic.RelatedObjectDoesNotExist:
            pass

        validated_data['rider_profile'] = self.context['request'].user.rider_profile
        return super().create(validated_data)

    class Meta:
        model = models.RiderProfileImage
        fields = '__all__'


class RiderProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RiderProfile
        fields = '__all__'


class VerifyUserSerializer(serializers.Serializer):

    token = serializers.CharField(required=True)

    def is_valid(self, raise_exception=False):
        super().is_valid(raise_exception)
        token = self.validated_data["token"]
        try:
            payload = decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except DecodeError:
            raise_validation_error({"detail": "Invalid token"})
        user = get_object_or_404(models.User, email=payload["email"])
        user.is_verified = True
        user.save()


class RiderLocationSerializer(serializers.Serializer):
    lat = serializers.DecimalField(decimal_places=6, max_digits=40)
    long = serializers.DecimalField(decimal_places=6, max_digits=40)

    def create(self, validated_data):
        lat = validated_data.pop('lat')
        long = validated_data.pop('long')
        rider_profile = self.context['request'].user.rider_profile
        instance, _ = models.CurrentRiderLocation.objects.get_or_create(rider_profile=rider_profile)
        instance.lat = lat
        instance.long = long
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = ['id', 'first_name', 'second_name']


class UpdateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, validators=[validate_password], write_only=True)

    def update(self, instance, validated_data):

        password = validated_data.get('password')
        
        if password:
            validated_data.pop('password')
            instance.set_password(password)

        return super().update(instance, validated_data)

    def create(self, validated_data):
        
        super().create(validated_data)

    class Meta:
        model = models.User
        fields = ['first_name', 'second_name', 'password', 'email', 'phone_no']
        extra_kwargs = {
            'password': {'write_only':True},
            }
