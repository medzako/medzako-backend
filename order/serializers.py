from rest_framework import serializers

from . import models
from medication.serializers import MedicationSerializer, MinimizedPharmacySerializer
from core.utils.helpers import generate_random_string


class ItemsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.OrderItem
        fields = '__all__'
        extra_kwargs = {
            'order': {'read_only':True},
        }


class FetchItemsSerializer(serializers.ModelSerializer):
    medication = MedicationSerializer()
    
    class Meta:
        model = models.OrderItem
        fields = '__all__'


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

        tracking_id = generate_random_string(12)
        tracking_info = {
            'order': instance,
            'lat': instance.pharmacy.location_lat,
            'long': instance.pharmacy.location_long,
            'tracking_id': tracking_id
        }
        
        models.CurrentOrderLocation.objects.create(**tracking_info)

        return instance
    
    class Meta:
        model = models.Order
        fields = '__all__'

class FetchOrderSerializer(serializers.ModelSerializer):

    pharmacy = MinimizedPharmacySerializer()
    
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

    def is_valid(self, raise_exception=False):

        if self.initial_data.get('event') == 'charge.completed':
           data = self.initial_data.get('data')
           data['event_id'] = data.get('id')
           customer = data.get('customer')
           if customer:
               customer_email = customer.get('email')
               customer_phone_no = customer.get('phone_number')
               data['customer_email'] = customer_email
               data['customer_phone_no'] = customer_phone_no
               

           self.initial_data = data

        raise_exception=False

        return super().is_valid(raise_exception=raise_exception)

    def save(self, **kwargs):
        instance =  super().save(**kwargs)
        order = models.Order.objects.filter(customer__email=instance.customer_email, payment=None).order_by('-id').first()
        if order:
            order.payment = instance
            order.is_payment_complete = True
            order.save()
        return instance

    class Meta:
        model = models.Payment
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        model = models.Location
        fields = '__all__'
        extra_kwargs = {
            'customer': {'read_only': True}
        }


class ImageUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Image
        fields = '__all__'


class RetrieveOrderSerializer(serializers.ModelSerializer):
    
    prescription = ImageUploadSerializer()
    location = LocationSerializer()
    pharmacy = MinimizedPharmacySerializer()
    
    class Meta:
        model = models.Order
        fields = '__all__'
