from django.db.models import fields
from rest_framework import serializers

from . import models


class ItemsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.OrderItem
        fields = '__all__'
        extra_kwargs = {
            'order': {'read_only':True},
        }


class OrderSerializer(serializers.ModelSerializer):
    items = serializers.ListField(child=ItemsSerializer(), allow_empty=False)

    def create(self, validated_data):
        items = validated_data.pop('items')
        validated_data['customer'] = self.context['request'].user
        instance = self.Meta.model._default_manager.create(**validated_data)

        for item in items:
            item['order'] = instance
            models.OrderItem._default_manager.create(**item)

        self.fields.pop('items')


        return instance
    
    class Meta:
        model = models.Order
        fields = '__all__'


class UpdateOrderSerializer(serializers.ModelSerializer):

    def save(self, **kwargs):
        instance =  super().save(**kwargs)
        if instance.is_completed:
            instance.pharmacy.completed_orders += 1
            instance.pharmacy.save()
            for item in instance.items.all():
                item.medication.units_moved += item.quantity
                item.medication.save()
        return instance
    
    class Meta:
        model = models.Order
        fields = ['is_completed', 'is_payment_complete']


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Payment
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Location
        fields = '__all__'
