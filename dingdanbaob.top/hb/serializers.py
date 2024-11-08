# hb/serializers.py
from rest_framework import serializers
from .models import Order, SecondLevelUser, PendingOrderRequest, Shop
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class ShopSerializer(serializers.ModelSerializer):
    second_level_users_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Shop
        fields = '__all__'


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class SecondLevelUserSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer()
    shops = ShopSerializer(many=True, read_only=True)
    blacklist_info = serializers.SerializerMethodField()

    class Meta:
        model = SecondLevelUser
        fields = '__all__'

    def get_blacklist_info(self, obj):
        # 获取用户的所有拉黑记录
        blacklists = obj.blacklist_set.all()
        reasons_count = {}
        total_blacklist_count = blacklists.count()

        # 遍历拉黑记录，统计每个原因的次数
        for blacklist in blacklists:
            reason = blacklist.get_reason_display()
            if reason in reasons_count:
                reasons_count[reason] += 1
            else:
                reasons_count[reason] = 1

        # 只返回非零的拉黑原因及总次数
        return {
            'total_blacklist_count': total_blacklist_count,
            'reasons': {reason: count for reason, count in reasons_count.items() if count > 0}
        }


class OrderSerializer(serializers.ModelSerializer):
    shop = ShopSerializer()
    first_level_user = serializers.CharField(source='first_level_user.user.username', read_only=True)
    blacklist_info = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'
        
    def get_blacklist_info(self, obj):
        # 获取订单购买用户的 Open UID
        buyer_open_uid = obj.buyer_open_uid
        if not buyer_open_uid:
            return None
        
        # 查询与该购买用户相关的黑名单记录
        blacklist_entries = Blacklist.objects.filter(buyer_open_uid=buyer_open_uid)
        total_blacklist_count = blacklist_entries.count()
        
        # 统计拉黑原因及次数
        reasons = {}
        for entry in blacklist_entries:
            reason = entry.get_reason_display()
            if reason in reasons:
                reasons[reason] += 1
            else:
                reasons[reason] = 1

        # 返回黑名单信息
        return {
            'total_blacklist_count': total_blacklist_count,
            'reasons': reasons
        }

    def create(self, validated_data):
        shop_data = validated_data.pop('shop')
        shop, created = Shop.objects.get_or_create(**shop_data)
        order = Order.objects.create(shop=shop, **validated_data)
        return order


class PendingOrderRequestSerializer(serializers.ModelSerializer):
    second_level_user = serializers.CharField(source='second_level_user.user.username', read_only=True)
    first_level_user = serializers.CharField(source='first_level_user.user.username', read_only=True)
    second_level_user_wechat_nickname = serializers.CharField(source='second_level_user.wechat_nickname',
                                                              read_only=True)

    class Meta:
        model = PendingOrderRequest
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], password=validated_data['password'])
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in with provided credentials.")


# 保留原有的UserSerializer
class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in with provided credentials.")


from rest_framework import serializers
from .models import BalanceChangeRecord

class BalanceChangeRecordSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = BalanceChangeRecord
        fields = '__all__'


from .models import Blacklist

class BlacklistSerializer(serializers.ModelSerializer):
    first_level_user_username = serializers.ReadOnlyField(source='first_level_user.user.username')
    second_level_user_username = serializers.ReadOnlyField(source='second_level_user.user.username')
    second_level_user_id = serializers.ReadOnlyField(source='second_level_user.id')  # 添加二级用户的 ID
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)

    class Meta:
        model = Blacklist
        fields = '__all__'
