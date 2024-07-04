from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import FirstLevelUser, Shop, SecondLevelUser, SecondLevelUserShop, Order, PendingOrderRequest

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
    list_display = ('order_number', 'amount', 'shop', 'status', 'add_time','tijiao')
    search_fields = ('order_number', 'shop__name')
    list_filter = ('shop', 'status')

@admin.register(PendingOrderRequest)
class PendingOrderRequestAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'second_level_user', 'add_time')
    search_fields = ('order_number', 'second_level_user__user__username')
    list_filter = ('add_time',)
