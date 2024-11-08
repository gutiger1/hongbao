# hb/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from .views import *

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'second_level_users', SecondLevelUserViewSet, basename='secondleveluser')
router.register(r'pending_order_requests', PendingOrderRequestViewSet, basename='pendingorderrequest')
router.register(r'shops', ShopViewSet, basename='shop')  # 添加 shops 路由
router.register(r'balance-change-records', BalanceChangeRecordViewSet, basename='balance-change-record')

urlpatterns = [
    path('register/', register),
    path('login/', login_view),
    path('user-info/', user_info),  # 新增 user-info 路由
    path('upload-order/', upload_order),  # 新增 upload-order 路由
    path('generate-event-link/', generate_event_link, name='generate_event_link'),
    path('wechat-auth/', wechat_auth, name='wechat_auth'),
    path('claim-order/', claim_order, name='claim_order'),
    path('add-shop/', add_shop, name='add_shop'),  # 新增添加店铺的路由
    path('second-level-users/', get_second_level_users, name='get_second_level_users'),
    path('manage-user-shop/', manage_user_shop, name='manage_user_shop'),
    path('shops/', ShopViewSet.as_view({'get': 'list'}), name='shops_list'),
    path('pending-orders/', get_pending_orders, name='get_pending_orders'),
    path('pending-orders/<int:pk>/', delete_pending_order, name='delete_pending_order'),
    path('pending-orders/batch-delete/', batch_delete_pending_orders, name='batch_delete_pending_orders'),
    path('orders/batch-delete/', batch_delete_orders, name='batch_delete_orders'),
    path('change-password/', change_password, name='change_password'),

    path('pending-order-requests/', get_pending_order_requests, name='get_pending_order_requests'),  # 新增路由
    path('completed-orders/', get_completed_orders, name='get_completed_orders'),  # 新增路由
    path('upload-image/', upload_image, name='upload_image'),
    path('delete-image/', delete_image, name='delete_image'),
    path('save-event/', save_event, name='save_event'),
    path('fetch-event/', fetch_event, name='fetch_event'),

    path('dashboard-stats/', get_dashboard_stats, name='get_dashboard_stats'),
    path('monthly-refunds/', get_monthly_refunds),
    path('daily-refunds/', get_daily_refunds, name='daily-refunds'),
    path('user-refund-ranking/', get_user_refund_ranking),
    path('log/', log_message, name='log_message'),

    path('authorize-auto-fetch/', authorize_auto_fetch, name='authorize_auto_fetch'),
    path('agiso-callback/', agiso_callback, name='agiso_callback'),
    path('agiso/order-push/', receive_order_push, name='receive_order_push'),
    path('cancel-auto-fetch/', cancel_auto_fetch, name='cancel_auto_fetch'),
    
    path('send-verification-code/', send_verification_code, name='send_verification_code'),
    
    path('send-reset-link/', send_reset_link, name='send_reset_link'),
    path('reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    
    path('generate-wechat-auth-link/', generate_wechat_auth_link, name='generate_wechat_auth_link'),
    
    path('notify/', wechat_pay_notify, name='wechat_pay_notify'),
    
    path('save-commission-method/', save_commission_method, name='save_commission_method'),
    
    path('user-shop-counts/', get_user_shop_counts, name='user-shop-counts'),
    
    path('add-to-blacklist/', add_to_blacklist, name='add_to_blacklist'),
    path('remove-from-blacklist/', remove_from_blacklist, name='remove_from_blacklist'),
    path('blacklist/', get_blacklist, name='get_blacklist'),
    
    path('use-activation-code/', use_activation_code, name='use_activation_code'),
    
    path('shops/<int:pk>/update-name/', ShopViewSet.as_view({'post': 'update_name'}), name='update_shop_name'),


    path('generate-invite-link/', generate_invite_link, name='generate_invite_link'),
    path('invite-info/', get_invite_info, name='get_invite_info'),
    

    path('', include(router.urls)),
]

# 在开发环境中提供静态和媒体文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
