from rest_framework import serializers
from .models import User, Order, Provider


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ()


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ()


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        exclude = ()
