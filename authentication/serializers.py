from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.utils.constants import USER_TYPES

from . import models

class RegistrationSerializer(serializers.ModelSerializer):

    user_type = serializers.ChoiceField(choices=USER_TYPES)

    def create(self, validated_data):
        user = models.User.objects.create_user(**validated_data)
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
        token['name'] = user.full_name
        token['is_admin'] = user.is_admin
        token['is_superuser'] = user.is_superuser
        return token

class PharmacyLicenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PharmacyLicense


class RiderLicenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RiderLicense


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
