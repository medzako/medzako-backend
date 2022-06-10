from decimal import Decimal
from email import message
from pyexpat import model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.db.utils import IntegrityError
from authentication.serializers import MinimizedUserSerializer, UserSerializer

from core.utils.constants import ACCEPTED, DELIVERED, DISPATCHED, RIDER
from medication.models import PharmacyStock

from . import models
from medication.serializers import MedicationSerializer, MinimizedPharmacySerializer
from core.utils.helpers import (generate_random_string, get_pharmacy_users, get_rider, raise_validation_error,
 send_order_customer_notifications, send_order_pharmacy_notifications, send_order_rider_notifications, 
 sendFCMMessage)


class ItemsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.OrderItem
        fields = ['quantity', 'price', 'medication']
        extra_kwargs = {
            'order': {'read_only':True},
        }


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
        

class FCMOrderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Order
        fields = '__all__'


class MinimizedPaymentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Payment
        fields = ['charged_amount', 'event_id', 'payment_type']


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
        send_order_pharmacy_notifications(instance, 'New Order', f'New order from {instance.customer.first_name} {instance.customer.second_name}')

        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        serializer = FCMOrderSerializer(instance=instance)
        sendFCMMessage.delay([instance.customer], serializer.data, 'Order Updated', 'The order has been updated')
        return instance
    
    class Meta:
        model = models.Order
        fields = '__all__'


class ImageUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Image
        fields = '__all__'


class FetchOrderSerializer(serializers.ModelSerializer):

    pharmacy = MinimizedPharmacySerializer()
    prescription = ImageUploadSerializer()
    customer = MinimizedUserSerializer()
    location = LocationSerializer()
    items = ItemsSerializer(many=True)
    
    class Meta:
        model = models.Order
        fields = '__all__'


class SocketOrderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Order
        fields = '__all__'


class MinimizedOrderSerializer(serializers.ModelSerializer):

    customer = MinimizedUserSerializer()
    items = ItemsSerializer(many=True)
    
    class Meta:
        model = models.Order
        fields = ['id', 'customer', 'total_price', 'status', 'items']


class MinimizedEarningOrderSerializer(serializers.ModelSerializer):

    items = ItemsSerializer(many=True)
    
    class Meta:
        model = models.Order
        fields = ['id', 'customer', 'total_price', 'status']


class ReOrderSerializer(serializers.ModelSerializer):
    order = serializers.IntegerField(required=True)

    def create(self, validated_data):
        self.fields.pop('order')
        order_id = validated_data.pop('order')
        order = get_object_or_404(models.Order, pk=order_id)
        if order.customer != self.context['request'].user:
            raise_validation_error({'detail': 'You cannot access this order'})

        validated_data['total_price'] = order.total_price
        validated_data['customer'] = self.context['request'].user
        validated_data['delivery_fee'] = order.delivery_fee
        validated_data['pharmacy'] = order.pharmacy
        validated_data['location'] = order.location

        instance = models.Order._default_manager.create(**validated_data)

        new_price = Decimal(0.0)
        not_in_stock = ""

        for itemInstance in order.items.all():
            stock_item = PharmacyStock.objects.get(pharmacy=order.pharmacy, medication=itemInstance.medication, in_stock=True)
            if not stock_item:
                not_in_stock += f'{itemInstance.medication.name}, '
                continue
            item_price = stock_item.price * itemInstance.quantity
            new_price += item_price
            
            item = {}
            item['quantity'] = itemInstance.quantity
            item['order'] = instance
            item['medication'] = itemInstance.medication
            item['price'] = item_price
            models.OrderItem._default_manager.create(**item)
        
        if not_in_stock:
            message = not_in_stock + ' medication are not in stock.'
            instance.delete()
            raise_validation_error({'detail': message})

        instance.total_price = new_price
        instance.save()    
        return instance

    class Meta:
        model = models.Order
        fields = ['id', 'pharmacy', 'total_price', 'order']
        extra_kwargs = {
            'id': {'read_only': True},
            'pharmacy': {'read_only': True},
            'total_price': {'read_only': True},
        }


class UpdateOrderSerializer(serializers.ModelSerializer):

    def is_valid(self, raise_exception=False):
        # if self.instance is not None and not self.instance.is_payment_complete:
        #     raise_validation_error({'detail': 'Invalid request. Customer payment not complete'})

        return super().is_valid(raise_exception)

    def save(self, **kwargs):
        instance =  super().save(**kwargs)
        if  instance.status == DELIVERED:
            try:
                models.OrderEarning.objects.create(order=instance, 
                pharmacy=instance.pharmacy, 
                pharmacy_earning=instance.total_price, rider_earning=50)
            except IntegrityError:
                raise_validation_error({'detail': 'Order completed already'})

            instance.rider.rider_profile.is_online = True
            instance.rider.rider_profile.save()
            instance.pharmacy.completed_orders += 1
            instance.pharmacy.save()
            for item in instance.items.all():
                item.medication.units_moved += item.quantity
                item.medication.save()

        if instance.status == ACCEPTED:
            pharmacy=instance.pharmacy
            rider = get_rider((pharmacy.location_lat, pharmacy.location_long))
            if rider:
                instance.rider = rider
                instance.save()
                rider_history_object = models.RiderHistory.objects.create(order=instance, rider=rider)

                send_order_rider_notifications(rider, instance, rider_history_object.id)
                send_order_pharmacy_notifications(instance)
                send_order_customer_notifications(instance)
            else:
                send_order_pharmacy_notifications(instance, title='Rider not Found', message='A rider has not been found at this time')

        if instance.status == DISPATCHED:
            if not instance.rider:
                raise_validation_error({'detail': 'You cannot dispatch order without rider'})

            rider_history_object = models.RiderHistory.objects.filter(order=instance.pk, rider=instance.rider.pk).latest('pk')

            send_order_customer_notifications(instance, title='Order Dispatched', message='Your order has been dispatched from the pharmacy')
            send_order_rider_notifications(instance.rider, instance, rider_history_object.id, title='Order Dispatched', message=f'Order {instance.id} has been dispatched') 

        return instance  
    
    class Meta:
        model = models.Order
        fields = ['is_completed', 'status', 'action_reason']


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

        raise_exception=True

        return super().is_valid(raise_exception=raise_exception)

    def save(self, **kwargs):
        instance =  super().save(**kwargs)
        order = models.Order.objects.filter(customer__email=instance.customer_email, is_payment_complete=False).order_by('-id').first()

        if order:
            order.payment = instance
            order.is_payment_complete = True
            order.save()
            users = []
            users.append(order.customer)
            users += get_pharmacy_users(order.pharmacy)
            notification_message = f'A payment of {instance.amount} has been received'
            title = 'Payment Complete'
            serializer = FCMOrderSerializer(instance=order)
            data = serializer.data
            if (hasattr(order, 'tracking_object')):
                data['tracking_id'] = order.tracking_object.tracking_id
            sendFCMMessage.delay(users, data, title, notification_message)

        return instance

    class Meta:
        model = models.Payment
        fields = '__all__'


class RetrieveOrderSerializer(serializers.ModelSerializer):
    
    prescription = ImageUploadSerializer()
    location = LocationSerializer()
    pharmacy = MinimizedPharmacySerializer()
    customer = UserSerializer()
    rider = UserSerializer()
    payment = MinimizedPaymentSerializer()
    items = FetchItemsSerializer(many=True)
    
    class Meta:
        model = models.Order
        fields = '__all__'


class RiderEarningsSerializer(serializers.ModelSerializer):

    order = MinimizedOrderSerializer()

    class Meta:
        model = models.OrderEarning
        fields = ['order', 'rider_earning']


class PharmacyEarningsSerializer(serializers.ModelSerializer):

    order = MinimizedOrderSerializer()

    class Meta:
        model = models.OrderEarning
        fields = ['order', 'pharmacy_earning']


class RiderHistorySerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        if instance.is_accepted != None:
            raise_validation_error({'detail': 'Order already accepted or rejected'})

        instance = super().update(instance, validated_data)

        def get_new_rider():   
            pharmacy=instance.order.pharmacy
            rider = get_rider((pharmacy.location_lat, pharmacy.location_long), order=instance.order)
            rider_history_object = models.RiderHistory.objects.create(order=instance.order, rider=rider)

            send_order_rider_notifications(rider, instance.order, rider_history_object.id)
        
        if instance.is_accepted==True:
            instance.order.rider=instance.rider
            instance.order.save()
            instance.rider.rider_profile.is_online =  False
            instance.rider.rider_profile.save()
            send_order_pharmacy_notifications(instance.order)
            
        elif instance.is_accepted==False:
            get_new_rider()

        return instance

    class Meta:
        model = models.RiderHistory
        fields = ['is_accepted']


class RetrieveRiderHistorySerializer(serializers.ModelSerializer):

    order = FCMOrderSerializer()

    class Meta:
        model = models.RiderHistory
        fields = '__all__'
        extra_kwargs = {
            'order': {'read_only': True}
        }


class RiderRatesSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RiderRating
        fields = '__all__'
        extra_kwargs = {
            'order': {'read_only': True},
            'rider': {'read_only': True},
            'customer': {'read_only': True}
        }


class PharmacyRatesSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PharmacyRating
        fields = '__all__'
        extra_kwargs = {
            'order': {'read_only': True},
            'pharmacy': {'read_only': True},
            'customer': {'read_only': True}
        }
