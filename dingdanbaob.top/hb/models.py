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
    email = models.EmailField(max_length=254, null=True, blank=True, verbose_name=_("邮箱"))  
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("账户余额")) 
    second_level_users = models.ManyToManyField('SecondLevelUser', through='FirstLevelUserSecondLevelUser',
                                                verbose_name=_("二级用户"), related_name="first_level_users")

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _("一级用户")
        verbose_name_plural = _("一级用户")

class Shop(BaseModel):
    owner = models.ForeignKey(FirstLevelUser, on_delete=models.CASCADE, verbose_name=_("所有者"))
    name = models.CharField(max_length=100, verbose_name=_("店铺名称"))
    approved = models.BooleanField(default=False, verbose_name=_("已审核"))
    
    # 自动获取订单相关字段
    auto_fetch_enabled = models.BooleanField(default=False, verbose_name=_("自动获取订单"))
    access_token = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("AccessToken"))
    tbnick = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("淘宝昵称"))

    # 佣金相关字段
    COMMISSION_METHOD_CHOICES = [
        ('fixed', '固定金额'),
        ('percentage', '比例佣金'),
        ('commission_and_principal', '佣金+本金'),
    ]
    commission_method = models.CharField(
        max_length=50, 
        choices=COMMISSION_METHOD_CHOICES, 
        default='percentage',  # 默认佣金方式为比例佣金
        verbose_name=_("佣金计算方式")
    )
    fixed_commission = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name=_("固定佣金金额")
    )
    percentage_commission = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True,  # 允许空值
        blank=True,  # 允许空值
        default=100,  # 默认比例为100%
        verbose_name=_("佣金百分比")
    )
    fixed_commission_with_principal = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name=_("佣金+本金固定佣金")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("店铺")
        verbose_name_plural = _("店铺")


class SecondLevelUser(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("用户"))
    shops = models.ManyToManyField(Shop, through='SecondLevelUserShop', verbose_name=_("店铺"))
    wechat_nickname = models.CharField(max_length=100, verbose_name=_("微信昵称"), blank=True, null=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _("二级用户")
        verbose_name_plural = _("二级用户")

    def get_shops_and_owners(self):
        return ", ".join([f"{shop.name} (Owner: {shop.owner.user.username})" for shop in self.shops.all()])
    get_shops_and_owners.short_description = _("店铺和所有者")

class FirstLevelUserSecondLevelUser(BaseModel):
    first_level_user = models.ForeignKey(FirstLevelUser, on_delete=models.CASCADE, verbose_name=_("一级用户"))
    second_level_user = models.ForeignKey(SecondLevelUser, on_delete=models.CASCADE, verbose_name=_("二级用户"))

    def __str__(self):
        return f"{self.first_level_user.user.username} - {self.second_level_user.user.username}"

    class Meta:
        verbose_name = _("一级用户和二级用户关联")
        verbose_name_plural = _("一级用户和二级用户关联")

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
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("佣金金额"))  # 最终发放的金额
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name=_("店铺"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("状态"))
    tijiao = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("提交人"))
    first_level_user = models.ForeignKey(FirstLevelUser, on_delete=models.CASCADE, verbose_name=_("一级用户"), null=True, blank=True)
    buyer_open_uid = models.CharField(max_length=100, blank=True, null=True, verbose_name="买家OpenUID") 
    wx_batch_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="微信支付批次号")

    def __str__(self):
        return self.order_number

    class Meta:
        verbose_name = _("订单")
        verbose_name_plural = _("订单")

    def mark_as_distributed(self):
        if self.status != 'distributed':  # 避免重复标记
            self.status = 'distributed'
            self.save()
        
        

    def mark_as_expired(self):
        self.status = 'expired'
        self.save()

class PendingOrderRequest(BaseModel):
    order_number = models.CharField(max_length=100, verbose_name=_("订单编号"))
    second_level_user = models.ForeignKey(SecondLevelUser, on_delete=models.CASCADE, verbose_name=_("二级用户"))
    first_level_user = models.ForeignKey(FirstLevelUser, on_delete=models.CASCADE, verbose_name=_("一级用户"))
    def __str__(self):
        return self.order_number

    class Meta:
        verbose_name = _("待处理订单请求")
        verbose_name_plural = _("待处理订单请求")


from django.db import models
from django.contrib.auth.models import User

class BalanceChangeRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    balance = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="账户余额")
    change_type = models.CharField(max_length=10, choices=[('支出', '支出'), ('入账', '入账')], verbose_name="业务类型")
    change_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="业务金额")
    time = models.DateTimeField(auto_now_add=True, verbose_name="时间")
    order_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="单号")

    def __str__(self):
        return f"{self.user.username} - {self.change_type} - {self.change_amount} - {self.time}"


class Event(models.Model):
    first_level_user = models.ForeignKey(FirstLevelUser, on_delete=models.CASCADE, verbose_name=_("一级用户"))
    title = models.CharField(max_length=100, verbose_name=_("活动标题"), default="返佣活动")
    image = models.URLField(max_length=200, verbose_name=_("广告说明图"), blank=True, null=True)
    command_title = models.CharField(max_length=100, verbose_name=_("口令标题"), default="口令")
    command_description = models.CharField(max_length=200, verbose_name=_("口令标题说明"), default="请输入口令")
    link = models.URLField(max_length=200, verbose_name=_("活动链接"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("创建时间"))

    def __str__(self):
        return self.title
        


class Blacklist(models.Model):
    REASON_CHOICES = [
        ('white_piao', '白嫖'),
        ('competition', '同行'),
        ('fraud', '欺诈'),
        ('bad_review', '差评'),
    ]
    
    first_level_user = models.ForeignKey(FirstLevelUser, on_delete=models.CASCADE, verbose_name="一级用户")
    second_level_user = models.ForeignKey(SecondLevelUser, on_delete=models.CASCADE, verbose_name="二级用户")
    buyer_open_uid = models.CharField(max_length=255, verbose_name="购买用户 buyer_open_uid", null=True, blank=True)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, verbose_name="拉黑原因")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="拉黑时间")

    def __str__(self):
        return f"{self.first_level_user.user.username} 拉黑了 {self.second_level_user.user.username} - {self.get_reason_display()}"

    class Meta:
        verbose_name = "黑名单"
        verbose_name_plural = "黑名单"
        unique_together = ['first_level_user', 'second_level_user']
        


class ActivationCode(models.Model):
    TYPE_CHOICES = [
        ('renew', '续费'),
        ('recharge', '充值')
    ]

    code = models.CharField(max_length=100, unique=True, verbose_name=_("激活码"))
    used_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='used_codes', verbose_name=_("使用者"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("生成时间"))
    used_at = models.DateTimeField(null=True, blank=True, verbose_name=_("使用时间"))
    is_used = models.BooleanField(default=False, verbose_name=_("是否已使用"))
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("激活码值（天数或金额）"))
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='renew', verbose_name=_("类型"))  # 设置默认值为 'renew'

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = get_random_string(length=12)  # 自动生成12位随机激活码
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} ({self.get_type_display()})"  # 显示激活码及其用途

    class Meta:
        verbose_name = _("激活码")
        verbose_name_plural = _("激活码")





from django.db import models
from .models import FirstLevelUser

class FirstLevelUserInvite(models.Model):
    inviter = models.ForeignKey(FirstLevelUser, related_name='invited', on_delete=models.CASCADE, verbose_name="邀请者")
    invitee = models.ForeignKey(FirstLevelUser, related_name='inviter', on_delete=models.CASCADE, verbose_name="被邀请者")
    rewarded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    rewarded_at = models.DateTimeField(null=True, blank=True, verbose_name="赠送时间")  # 记录赠送奖励的时间

    class Meta:
        unique_together = ('inviter', 'invitee')
        verbose_name = "一级用户邀请关系"
        verbose_name_plural = "一级用户邀请关系"

    def __str__(self):
        return f"{self.inviter.user.username} 邀请了 {self.invitee.user.username}"














# 记录一级用户 二级用户 购买用户的关联关系s


from django.db import models

class UserAssociation(models.Model):
    first_level_user = models.ForeignKey(FirstLevelUser, on_delete=models.CASCADE, verbose_name="一级用户")
    second_level_user = models.ForeignKey(SecondLevelUser, on_delete=models.CASCADE, verbose_name="二级用户")
    buyer_open_uid = models.CharField(max_length=255, verbose_name="购买用户 buyer_open_uid")  # 购买用户ID
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="关联时间")

    class Meta:
        verbose_name = "用户关联"
        verbose_name_plural = "用户关联"
        unique_together = ['first_level_user', 'second_level_user', 'buyer_open_uid']

    def __str__(self):
        return f"{self.first_level_user.user.username} - {self.second_level_user.user.username} - {self.buyer_open_uid}"

# 记录一级用户 二级用户 购买用户的关联关系s