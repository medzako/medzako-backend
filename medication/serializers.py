from rest_framework import serializers
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
