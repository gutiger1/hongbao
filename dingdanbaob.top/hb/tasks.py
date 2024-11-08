from celery import shared_task
from django.utils import timezone
from hb.models import FirstLevelUser, Shop
from hb.views import agiso_cancel_authorization
import logging

logger = logging.getLogger(__name__)

@shared_task
def check_expired_users():
    logger.info("开始检查过期用户...")
    now = timezone.now()
    expired_users = FirstLevelUser.objects.filter(expiration_date__lte=now)
    logger.info(f"找到 {expired_users.count()} 个过期用户")

    if not expired_users.exists():
        logger.info("没有找到过期的用户。")
        return

    for user in expired_users:
        logger.info(f"检查过期用户: {user.user.username} (ID: {user.id})")

        shops = Shop.objects.filter(owner=user, auto_fetch_enabled=True)
        logger.info(f"用户 {user.user.username} 有 {shops.count()} 个启用自动获取订单的店铺")

        for shop in shops:
            logger.info(f"尝试取消店铺 {shop.name} 的自动获取订单功能")
            logger.debug(f"Invoking agiso_cancel_authorization for shop with ID: {shop.id}")
            logger.debug(f"Shop access_token: {shop.access_token}")
            logger.debug(f"Shop auto_fetch_enabled: {shop.auto_fetch_enabled}")
            result = agiso_cancel_authorization(shop)

            if 'success' in result:
                logger.info(f"成功取消店铺 {shop.name} 的自动获取订单功能")
            else:
                logger.error(f"无法取消店铺 {shop.name} 的自动获取订单功能: {result.get('error')}")
