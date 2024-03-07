from rest_framework import serializers
from django.contrib.auth.models import Group, User
from svh_service.models import Consignment, Carpass, Contact


class IsAliveSerializer(serializers.Serializer):
    current_datetime = serializers.DateTimeField()
    app_name = serializers.CharField(max_length=20)
    is_alive = serializers.BooleanField()


class StatSerializer(serializers.Serializer):
    current_datetime = serializers.DateTimeField()
    consignments = serializers.IntegerField()
    carpass = serializers.IntegerField()
    contacts = serializers.IntegerField()
    documents = serializers.IntegerField()
    uemails = serializers.IntegerField()


# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'last_login', 'is_superuser', 'username', 'is_active']
    