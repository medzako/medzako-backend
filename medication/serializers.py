from rest_framework import serializers

from core.utils.helpers import raise_validation_error
from . import models
import medication

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

    class Meta:
        model = models.Pharmacy
        fields = '__all__'

    
class SinglePharmacySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Pharmacy
        fields = '__all__'

class MinimizedPharmacySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Pharmacy
        fields = ['id', 'name']


class RatesSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Rating
        fields = '__all__'


class StockSerializer(serializers.ModelSerializer):
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
    pharmacy = PharmacySerializer()

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
    medication = serializers.IntegerField()


    def create(self, validated_data):
        in_stock = validated_data.pop('in_stock')
        pharmacy = self.context['request'].user.pharmacist_profile.pharmacy
        if not pharmacy:
            raise_validation_error({"detail": "Create pharmacy first"})
        instance = models.PharmacyStock.objects.get_or_create(**validated_data, pharmacy=pharmacy.pk)
        instance.in_stock = in_stock
        instance.save()
        return instance
