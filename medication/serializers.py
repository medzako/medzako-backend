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


class PharmacySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Pharmacy
        fields = '__all__'

    
class SinglePharmacySerializer(serializers.ModelSerializer):
    medication = MedicationSerializer(many=True)

    class Meta:
        model = models.Pharmacy
        fields = '__all__'
        extra_kwargs = {
            'meddication': {'read_only':True},
        }


class RatesSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Rating
        fields = '__all__'
