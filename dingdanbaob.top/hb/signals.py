from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Order, PendingOrderRequest, FirstLevelUser, BalanceChangeRecord ,UserAssociation,Blacklist
from .utils import transfer_to_wechat_v3
import logging

logger = logging.getLogger(__name__)

def calculate_commission(shop, order_amount):
    """
    根据店铺的佣金计算方式计算佣金。
    """
    if shop.commission_method == 'fixed':
        return shop.fixed_commission or 0
    elif shop.commission_method == 'percentage':
        return (shop.percentage_commission or 100) * order_amount / 100
    elif shop.commission_method == 'commission_and_principal':
        return (shop.fixed_commission_with_principal or 0) + order_amount
    else:
        return order_amount

@receiver(post_save, sender=Order)
def process_pending_order_requests(sender, instance, created, **kwargs):
    if created:
        logger.debug(f"Processing pending order requests for order: {instance.order_number}")
        pending_requests = PendingOrderRequest.objects.filter(order_number=instance.order_number)
        for request in pending_requests:
            logger.debug(f"Found pending request: {request.id} for order: {instance.order_number}")

            second_level_user = request.second_level_user
            first_level_user = instance.first_level_user
            shop = instance.shop
            
            # 检查 buyer_open_uid 是否在黑名单中
            if Blacklist.objects.filter(first_level_user=first_level_user, buyer_open_uid=instance.buyer_open_uid).exists():
                logger.warning(f"Buyer {instance.buyer_open_uid} is blacklisted for first level user {first_level_user.user.username}")
                continue  # 跳过该订单的处理
            # 订单核销逻辑
            if shop in second_level_user.shops.all() and shop.approved:
                logger.debug(f"Shop is approved and associated with second level user: {second_level_user.user.username}")

                if first_level_user.balance >= instance.amount:
                    first_level_user.balance -= instance.amount
                    first_level_user.save()

                    # 创建 BalanceChangeRecord
                    BalanceChangeRecord.objects.create(
                        user=first_level_user.user,
                        balance=first_level_user.balance,
                        change_type='支出',
                        change_amount=instance.commission_amount,
                        time=timezone.now(),
                        order_number=instance.order_number
                    )

                    # 更新提交人字段
                    instance.tijiao = second_level_user.user.username
                    instance.mark_as_distributed()
                    
                    

                    # 计算佣金并保存到订单
                    commission = calculate_commission(shop, instance.amount)
                    instance.commission_amount = commission  # 保存佣金金额
                    instance.save()
                    logger.debug(f"Calculated commission for shop: {commission} 元")

                    # 调用微信转账接口
                    try:
                        amount_in_cents = int(commission * 100)  # 将佣金转换为分
                        logger.debug(f"开始处理佣金转账给二级用户: {second_level_user.user.username}, 金额: {amount_in_cents} 分")

                        result = transfer_to_wechat_v3(
                            partner_trade_no=instance.order_number,
                            openid=second_level_user.user.username,
                            amount=amount_in_cents,
                            desc=f"订单号 {instance.order_number} 的佣金"
                        )

                        if result["status"] == "success" and result.get("batch_id"):
                            logger.debug(f"Received batch_id: {result.get('batch_id')} from WeChat transfer")
                            instance.wx_batch_id = result.get("batch_id")  # 保存微信批次号到订单
                            instance.save()
                            logger.debug(f"Successfully saved wx_batch_id: {instance.wx_batch_id} for order: {instance.order_number}")
                        else:
                            logger.error(f"转账失败: {result}")

                    except Exception as e:
                        logger.error(f"转账失败: {str(e)}")

                    # 删除待处理请求
                    request.delete()
                    logger.debug(f"Order {instance.order_number} marked as distributed and pending request {request.id} deleted.")
                    
                    # 记录用户关联关系
                    UserAssociation.objects.get_or_create(
                        first_level_user=first_level_user,
                        second_level_user=second_level_user,
                        buyer_open_uid=instance.buyer_open_uid  # 替换为购买用户的 buyer_open_uid
                    )
                    
                else:
                    logger.warning('账户余额不足，请及时充值。')
            else:
                logger.warning(f"Shop {instance.shop.name} is not associated with second level user {second_level_user.user.username} or not approved.")


@receiver(post_save, sender=PendingOrderRequest)
def check_and_process_order(sender, instance, created, **kwargs):
    if created:
        logger.debug(f"Processing pending order request: {instance.id} for order: {instance.order_number}")
        try:
            order = Order.objects.get(order_number=instance.order_number)
            
            # 检查 buyer_open_uid 是否在黑名单中
            if Blacklist.objects.filter(first_level_user=order.first_level_user, buyer_open_uid=order.buyer_open_uid).exists():
                logger.warning(f"Buyer {order.buyer_open_uid} is blacklisted for first level user {order.first_level_user.user.username}")
                return  # 停止处理该订单
            
            if order.shop in instance.second_level_user.shops.all() and order.shop.approved and order.status == 'pending':
                logger.debug(f"Order {order.order_number} is pending, shop is approved and associated with second level user.")

                first_level_user = order.first_level_user
                if first_level_user.balance >= order.amount:
                    first_level_user.balance -= order.amount
                    first_level_user.save()

                    # 创建 BalanceChangeRecord
                    BalanceChangeRecord.objects.create(
                        user=first_level_user.user,
                        balance=first_level_user.balance,
                        change_type='支出',
                        change_amount=order.commission_amount,
                        time=timezone.now(),
                        order_number=order.order_number
                    )

                    # 新增提交人字段
                    order.tijiao = instance.second_level_user.user.username

                    order.mark_as_distributed()

                    # 计算佣金并保存到订单
                    commission = calculate_commission(order.shop, order.amount)
                    order.commission_amount = commission  # 保存佣金金额
                    order.save()
                    logger.debug(f"Calculated commission for shop: {commission} 元")

                    # 调用微信转账接口，将佣金金额转换为整数（单位为“分”）
                    try:
                        amount_in_cents = int(commission * 100)  # 将佣金转换为分
                        result = transfer_to_wechat_v3(
                            partner_trade_no=order.order_number,
                            openid=instance.second_level_user.user.username,
                            amount=amount_in_cents,
                            desc=f"订单号 {order.order_number} 的佣金"
                        )

                        if result["status"] == "success" and result.get("batch_id"):
                            logger.debug(f"Received batch_id: {result.get('batch_id')} from WeChat transfer")
                            order.wx_batch_id = result.get("batch_id")  # 保存微信支付批次号到订单
                            order.save()
                            logger.debug(f"Successfully saved wx_batch_id: {order.wx_batch_id} for order: {order.order_number}")
                        else:
                            logger.error(f"转账失败: {result}")

                    except Exception as e:
                        logger.error(f"转账失败: {str(e)}")

                    # 删除待处理请求
                    instance.delete()
                    logger.debug(f"Order {order.order_number} marked as distributed and pending request {instance.id} deleted.")
                    
                    # 记录用户关联关系，避免重复
                    UserAssociation.objects.get_or_create(
                        first_level_user=first_level_user,
                        second_level_user=instance.second_level_user,
                        buyer_open_uid=order.buyer_open_uid  # 购买用户的 buyer_open_uid
                    )
                else:
                    logger.warning('账户余额不足，请及时充值。')
            else:
                logger.warning(f"Order {order.order_number} cannot be processed. Either shop not approved or not associated with second level user.")
        except Order.DoesNotExist:
            # 如果订单不存在，保持待处理请求
            logger.error(f"Order {instance.order_number} does not exist.")
