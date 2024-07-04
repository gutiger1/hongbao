# hb/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, SecondLevelUserViewSet, PendingOrderRequestViewSet, ShopViewSet, user_info, upload_order
from hb.views import register, login_view
from django.conf.urls.static import static
from django.conf import settings
from .views import *

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'second_level_users', SecondLevelUserViewSet, basename='secondleveluser')
router.register(r'pending_order_requests', PendingOrderRequestViewSet, basename='pendingorderrequest')
router.register(r'shops', ShopViewSet, basename='shop')  # 添加 shops 路由

urlpatterns = [
    path('register/', register),
    path('login/', login_view),
    path('user-info/', user_info),  # 新增 user-info 路由
    path('upload-order/', upload_order),  # 新增 upload-order 路由
    path('generate-event-link/', generate_event_link, name='generate_event_link'),
    path('wechat-auth/', wechat_auth, name='wechat_auth'),
    path('claim-order/', claim_order, name='claim_order'),
    path('', include(router.urls)),
]

# 在开发环境中提供静态和媒体文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
