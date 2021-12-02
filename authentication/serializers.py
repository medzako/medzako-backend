from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from . import models

class RegistrationSerializer(serializers.ModelSerializer):

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
