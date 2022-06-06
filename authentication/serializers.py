from datetime import datetime, timedelta
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
        extra_kwargs = {
            'user': {'read_only':True},
            'is_approved': {'read_only':True},
        }


class AdminRiderProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RiderProfile
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only':True},
        }


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
        rider = self.context['request'].user
        instance, _ = models.CurrentRiderLocation.objects.get_or_create(rider=rider)
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

class PasswordResetSerializer(serializers.Serializer):

    email = serializers.EmailField()

    def is_user_available(self):
        email = self.validated_data.get("email")
        users = models.User.objects.filter(email=email)
        return users.exists()

    def create(self, validated_data):
        email = validated_data.pop("email")
        user = get_object_or_404(models.User, email)
        validated_data["user"] = user
        instance = models.ResetPasswordToken(**validated_data)
        instance.save()
        return instance


class UpdatePasswordSerializer(serializers.Serializer):

    confirm_password = serializers.CharField(validators=[validate_password])
    password = serializers.CharField(validators=[validate_password])
    token = serializers.CharField()

    def is_valid(self, raise_exception=True):
        super().is_valid(raise_exception=raise_exception)
        if not self.validated_data["confirm_password"] == self.initial_data["password"]:
            raise_validation_error({"detail":"Passwords do not match"})
        
        token = self.validated_data["token"]
        tokens = models.ResetPasswordToken.objects.filter(key=token)

        if not tokens.exists():
            raise_validation_error({"detail": "Invalid token"})

        if datetime.now() - tokens[0].created_at.replace(tzinfo=None)  > timedelta(hours=24):
            raise_validation_error({"detail": "Token expired"})

    def update_password(self):
        token = self.validated_data["token"]
        tokenObject = models.ResetPasswordToken.objects.get(key=token)
        user = tokenObject.user
        user.set_password(self.validated_data["password"])
        user.save()
        tokenObject.delete()
