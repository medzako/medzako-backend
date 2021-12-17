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

    def create(self, validated_data):
        instance = super().create(validated_data)
        profile = self.context['request'].user.pharmacist_profile
        profile.pharmacy = instance
        profile.save()
        return instance

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
