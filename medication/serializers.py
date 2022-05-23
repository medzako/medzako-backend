from rest_framework import serializers
from authentication.models import User
from core.utils.constants import PHARMACIST

from core.utils.helpers import raise_validation_error
from . import models


class MedicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Medication
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = '__all__'


class SingleMedicationSerializer(serializers.ModelSerializer):

    category = CategorySerializer()

    class Meta:
        model = models.Medication
        fields = '__all__'
        extra_kwargs = {
            'category': {
                'write_only': True
            }
        }


class PharmacySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)

    def create(self, validated_data):
        user = validated_data.pop('user')
        profile = user.pharmacist_profile
        if profile.pharmacy:
            raise_validation_error({'detail': 'User already registered to a pharmacy'})
        self.fields.pop('user')
        if user.user_type != PHARMACIST:
            raise_validation_error({'detail': 'User must be of pharmacist usertype'})
        instance = super().create(validated_data)
        profile.pharmacy = instance
        profile.save()
        return instance

    class Meta:
        model = models.Pharmacy
        fields = '__all__'
        extra_kwargs = {
            'user': {
                'write_only': True
            }
        }


class FetchPharmacySerializer(serializers.ModelSerializer):


    class Meta:
        model = models.Pharmacy
        fields = ['id', 'location_lat', 'location_long', 'location_name', 'name', 'image']

    
class SinglePharmacySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Pharmacy
        fields = '__all__'

class MinimizedPharmacySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Pharmacy
        fields = ['id', 'name', 'location_lat', 'location_long']


class GetStockSerializer(serializers.ModelSerializer):
    medication = SingleMedicationSerializer()

    class Meta:
        model = models.PharmacyStock
        fields = '__all__'
        extra_kwargs = {
            'medication': {
                'write_only': True
            }
        }

class SearchStockSerializer(serializers.ModelSerializer):
    medication = MedicationSerializer()

    class Meta:
        model = models.PharmacyStock
        fields = '__all__'
        extra_kwargs = {
            'medication': {
                'write_only': True
            }
        }


class MedicationStockSerializer(serializers.ModelSerializer):
    pharmacy = FetchPharmacySerializer()

    class Meta:
        model = models.PharmacyStock
        fields = '__all__'
        extra_kwargs = {
            'pharmacy': {
                'write_only': True
            }
        }


class StockSerializer(serializers.Serializer):
    in_stock = serializers.BooleanField()
    medication = serializers.PrimaryKeyRelatedField(queryset=models.Medication.objects.all())
    price = serializers.DecimalField(decimal_places=2, max_digits=9)

    def create(self, validated_data):
        in_stock = validated_data.pop('in_stock')
        price = validated_data.pop('price')
        pharmacy = self.context['request'].user.pharmacist_profile.pharmacy
        if not pharmacy:
            raise_validation_error({"detail": "Create pharmacy first"})
        instance, _ = models.PharmacyStock.objects.get_or_create(**validated_data, pharmacy=pharmacy)
        instance.in_stock = in_stock
        instance.price = price
        instance.save()
        return instance
