from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class BaseModel(models.Model):
    add_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class FirstLevelUser(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("用户"))
    expiration_date = models.DateTimeField(null=True, blank=True,verbose_name=_("到期时间"))
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("账户余额"))  # 新增字段

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _("一级用户")
        verbose_name_plural = _("一级用户")

class Shop(BaseModel):
    owner = models.ForeignKey(FirstLevelUser, on_delete=models.CASCADE, verbose_name=_("所有者"))
    name = models.CharField(max_length=100, verbose_name=_("店铺名称"))
    approved = models.BooleanField(default=False, verbose_name=_("已审核"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("店铺")
        verbose_name_plural = _("店铺")

class SecondLevelUser(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("用户"))
    shops = models.ManyToManyField(Shop, through='SecondLevelUserShop', verbose_name=_("店铺"))

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _("二级用户")
        verbose_name_plural = _("二级用户")

    def get_shops_and_owners(self):
        return ", ".join([f"{shop.name} (Owner: {shop.owner.user.username})" for shop in self.shops.all()])
    get_shops_and_owners.short_description = _("店铺和所有者")

class SecondLevelUserShop(BaseModel):
    second_level_user = models.ForeignKey(SecondLevelUser, on_delete=models.CASCADE, verbose_name=_("二级用户"))
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name=_("店铺"))

    def __str__(self):
        return f"{self.second_level_user} - {self.shop}"

    class Meta:
        verbose_name = _("二级用户店铺关联")
        verbose_name_plural = _("二级用户店铺关联")

class Order(BaseModel):
    STATUS_CHOICES = [
        ('pending', _("待发放")),
        ('distributed', _("已发放")),
        ('expired', _("已过期")),
    ]

    order_number = models.CharField(max_length=100, verbose_name=_("订单编号"),unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("订单金额"))
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name=_("店铺"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("状态"))
    tijiao = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("提交人"))
    first_level_user = models.ForeignKey(FirstLevelUser, on_delete=models.CASCADE, verbose_name=_("一级用户"), null=True, blank=True)

    def __str__(self):
        return self.order_number

    class Meta:
        verbose_name = _("订单")
        verbose_name_plural = _("订单")

    def mark_as_distributed(self):
        self.status = 'distributed'
        self.save()

    def mark_as_expired(self):
        self.status = 'expired'
        self.save()

class PendingOrderRequest(BaseModel):
    order_number = models.CharField(max_length=100, verbose_name=_("订单编号"))
    second_level_user = models.ForeignKey(SecondLevelUser, on_delete=models.CASCADE, verbose_name=_("二级用户"))

    def __str__(self):
        return self.order_number

    class Meta:
        verbose_name = _("待处理订单请求")
        verbose_name_plural = _("待处理订单请求")
