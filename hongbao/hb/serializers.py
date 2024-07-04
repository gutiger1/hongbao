# hb/serializers.py
from rest_framework import serializers
from .models import Order, SecondLevelUser, PendingOrderRequest, Shop

class ShopSerializer(serializers.ModelSerializer):
    second_level_users_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Shop
        fields = '__all__'
class OrderSerializer(serializers.ModelSerializer):
    shop = ShopSerializer()
    first_level_user = serializers.CharField(source='first_level_user.user.username', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        shop_data = validated_data.pop('shop')
        shop, created = Shop.objects.get_or_create(**shop_data)
        order = Order.objects.create(shop=shop, **validated_data)
        return order

class SecondLevelUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondLevelUser
        fields = '__all__'

class PendingOrderRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingOrderRequest
        fields = '__all__'

# 新增
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], password=validated_data['password'])
        return user

class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in with provided credentials.")
