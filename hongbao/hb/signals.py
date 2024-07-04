from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, PendingOrderRequest, FirstLevelUser

@receiver(post_save, sender=Order)
def process_pending_order_requests(sender, instance, created, **kwargs):
    if created:
        pending_requests = PendingOrderRequest.objects.filter(order_number=instance.order_number)
        for request in pending_requests:

            second_level_user = request.second_level_user
            first_level_user = instance.first_level_user

            if instance.shop in second_level_user.shops.all():

                if first_level_user.balance >= instance.amount:
                    first_level_user.balance -= instance.amount
                    first_level_user.save()

                    # /新增提交人字段
                    instance.tijiao = second_level_user.user.username

                    instance.mark_as_distributed()

                    # 这里可以添加代码将订单金额发送到二级用户的微信
                    request.delete()

                else:
                    print('账户余额不足，请及时充值。')


@receiver(post_save, sender=PendingOrderRequest)
def check_and_process_order(sender, instance, created, **kwargs):
    if created:
        try:
            order = Order.objects.get(order_number=instance.order_number)
            if order.shop in instance.second_level_user.shops.all() and order.status == 'pending':

                first_level_user = order.first_level_user
                if first_level_user.balance >= order.amount:
                    first_level_user.balance -= order.amount
                    first_level_user.save()
                    # 新增提交人字段
                    order.tijiao = instance.second_level_user.user.username

                    order.mark_as_distributed()
                    # 这里可以添加代码将订单金额发送到二级用户的微信
                    instance.delete()
                else:
                    print('账户余额不足，请及时充值。')
        except Order.DoesNotExist:
            # 如果订单不存在，保持待处理请求
            pass