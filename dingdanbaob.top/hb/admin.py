from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import FirstLevelUser, Shop, SecondLevelUser, SecondLevelUserShop, Order, PendingOrderRequest,FirstLevelUserSecondLevelUser

@admin.register(FirstLevelUser)
class FirstLevelUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'expiration_date', 'get_shops')
    search_fields = ('user__username',)

    def get_shops(self, obj):
        return ", ".join([shop.name for shop in obj.shop_set.all()])
    get_shops.short_description = _("名下店铺")

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'approved')
    search_fields = ('name', 'owner__user__username')
    list_filter = ('approved',)

@admin.register(SecondLevelUser)
class SecondLevelUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_shops_and_owners')
    search_fields = ('user__username',)

    def get_shops_and_owners(self, obj):
        return obj.get_shops_and_owners()
    get_shops_and_owners.short_description = _("店铺和所有者")

@admin.register(SecondLevelUserShop)
class SecondLevelUserShopAdmin(admin.ModelAdmin):
    list_display = ('second_level_user', 'shop')
    search_fields = ('second_level_user__user__username', 'shop__name')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'amount', 'shop', 'status', 'add_time','tijiao','first_level_user')
    search_fields = ('order_number', 'shop__name')
    list_filter = ('shop', 'status')

@admin.register(PendingOrderRequest)
class PendingOrderRequestAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'second_level_user','first_level_user', 'add_time')
    search_fields = ('order_number', 'second_level_user__user__username')
    list_filter = ('add_time',)


@admin.register(FirstLevelUserSecondLevelUser)
class FirstLevelUserSecondLevelUserAdmin(admin.ModelAdmin):
    list_display = ('first_level_user', 'second_level_user', 'add_time')
    search_fields = ('first_level_user__user__username', 'second_level_user__user__username')
    list_filter = ('add_time',)









from django.utils.crypto import get_random_string
from django.contrib import admin
from .models import ActivationCode

@admin.register(ActivationCode)
class ActivationCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'type', 'used_by', 'created_at', 'used_at', 'is_used', 'value')
    search_fields = ('code', 'used_by__username')
    list_filter = ('is_used', 'created_at', 'used_at', 'type')

    # 设置激活码的初始值（随机生成），以及用途和默认有效期
    def get_changeform_initial_data(self, request):
        initial_data = super().get_changeform_initial_data(request)
        initial_data['code'] = get_random_string(12)  # 默认生成12位随机激活码
        initial_data['type'] = 'renew'  # 默认用途是续费
        initial_data['value'] = 365  # 默认延长期限为365天
        return initial_data

    def save_model(self, request, obj, form, change):
        if not obj.code:
            obj.code = get_random_string(12)
        obj.value = obj.value or 365
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_staff
