import os

from django.db.models import Count
from .models import Order, SecondLevelUser, PendingOrderRequest, FirstLevelUser, FirstLevelUserSecondLevelUser, Event,Shop,Blacklist
from .serializers import OrderSerializer, SecondLevelUserSerializer, PendingOrderRequestSerializer,ShopSerializer
from rest_framework import viewsets, permissions, status
from .serializers import OrderSerializer
from decimal import Decimal

from rest_framework.pagination import PageNumberPagination

class OrderPagination(PageNumberPagination):
    page_size = 10  # 每页默认显示10条数据
    page_size_query_param = 'page_size'  # 支持通过查询参数设置每页大小
    max_page_size = 100  # 每页最多显示100条数据
    
    
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = OrderPagination  # 启用分页

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return Order.objects.none()
        try:
            first_level_user = FirstLevelUser.objects.get(user=user)
        except FirstLevelUser.DoesNotExist:
            return Order.objects.none()
        
        # 获取请求中的订单状态筛选参数
        status_filter = self.request.query_params.get('status', 'pending')  # 默认过滤 pending 状态
        queryset = Order.objects.filter(first_level_user=first_level_user, status=status_filter)

        # 处理筛选条件
        order_number = self.request.query_params.get('order_number')
        shop_name = self.request.query_params.get('shop')
        tijiao = self.request.query_params.get('tijiao')
        buyer_open_uid = self.request.query_params.get('buyer_open_uid')
        wx_batch_id = self.request.query_params.get('wx_batch_id')
        
        if order_number:
            queryset = queryset.filter(order_number__icontains=order_number)
        if shop_name:
            queryset = queryset.filter(shop__name__icontains=shop_name)
        if tijiao:
            queryset = queryset.filter(tijiao__icontains=tijiao)
        if buyer_open_uid:
            queryset = queryset.filter(buyer_open_uid__icontains=buyer_open_uid)
        if wx_batch_id:
            queryset = queryset.filter(wx_batch_id__icontains=wx_batch_id)

        # 按更新时间倒序排列
        return queryset.order_by('-update_time')

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            shop = Shop.objects.get(id=data['shop'])
            first_level_user = FirstLevelUser.objects.get(user=request.user)
            amount = Decimal(data['amount'])
            buyer_open_uid = data.get('buyer_open_uid')

            # 根据店铺的佣金计算模式计算 commission_amount
            if shop.commission_method == 'fixed':
                commission_amount = shop.fixed_commission
            elif shop.commission_method == 'percentage':
                commission_amount = amount * (shop.percentage_commission / 100)
            elif shop.commission_method == 'commission_and_principal':
                commission_amount = amount + shop.fixed_commission_with_principal
            else:
                commission_amount = amount

            # 创建订单时保存计算后的佣金金额
            order = Order.objects.create(
                order_number=data['order_number'],
                amount=amount,
                commission_amount=commission_amount,  # 保存佣金金额
                shop=shop,
                first_level_user=first_level_user,
                buyer_open_uid=buyer_open_uid
            )

            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Shop.DoesNotExist:
            return Response({'error': '店铺不存在'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action  # 确保导入了 @action
from rest_framework.response import Response
from .models import Shop, FirstLevelUser
from .serializers import ShopSerializer
from django.db.models import Count

class ShopViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ShopSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return Shop.objects.none()
        try:
            first_level_user = FirstLevelUser.objects.get(user=user)
        except FirstLevelUser.DoesNotExist:
            return Shop.objects.none()
        return Shop.objects.filter(owner=first_level_user).annotate(
            second_level_users_count=Count('secondlevelusershop'))

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = ShopSerializer(queryset, many=True).data
        return Response(data)

    @action(detail=True, methods=['post'], url_path='update-name')
    def update_name(self, request, pk=None):
        shop_id = pk
        new_name = request.data.get('name')
        if not new_name:
            return Response({'error': '新店铺名称不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            shop = Shop.objects.get(id=shop_id)
            first_level_user = FirstLevelUser.objects.get(user=request.user)
            if shop.owner != first_level_user:
                return Response({'error': '没有权限修改此店铺'}, status=status.HTTP_403_FORBIDDEN)

            shop.name = new_name
            shop.save()

            return Response({'success': '店铺名称已更新'}, status=status.HTTP_200_OK)

        except Shop.DoesNotExist:
            return Response({'error': '店铺不存在'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class SecondLevelUserViewSet(viewsets.ModelViewSet):
    queryset = SecondLevelUser.objects.all()
    serializer_class = SecondLevelUserSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('blacklist_set')
        return queryset

class PendingOrderRequestViewSet(viewsets.ModelViewSet):
    queryset = PendingOrderRequest.objects.all()
    serializer_class = PendingOrderRequestSerializer

# 新增

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


# 邮箱验证码注册s
import ssl
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from django.core.cache import cache
from django.utils.crypto import get_random_string
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def send_verification_code(request):
    email = request.data.get('email')

    if not email:
        logger.error("邮箱地址为空")
        return Response({'error': '邮箱是必需的'}, status=400)

    if User.objects.filter(email=email).exists():
        logger.warning(f"邮箱已被注册: {email}")
        return Response({'error': '该邮箱已被注册'}, status=400)

    # 生成随机验证码
    code = get_random_string(length=6, allowed_chars='0123456789')
    logger.info(f"生成的验证码为: {code}")

    # 将验证码存储在缓存中，有效期5分钟
    cache.set(email, code, timeout=300)
    logger.info(f"验证码存储在缓存中，邮箱: {email}, 验证码: {code}")

    subject = '您的验证码'
    message = f'您的验证码是 {code}'
    from_email = '1500133824@qq.com'
    password = 'ouhjchhhzpzzffeh'  # 请替换为实际的QQ邮箱授权码
    recipient_list = [email]

    try:
        # 创建邮件消息
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = from_email
        msg['To'] = ','.join(recipient_list)

        # 配置 SSL 上下文
        ssl_context = ssl.create_default_context(cafile='/etc/ssl/certs/ca-certificates.crt')

        # 使用 smtplib 发送邮件
        with smtplib.SMTP_SSL('smtp.qq.com', 465, context=ssl_context) as server:
            server.login(from_email, password)
            server.sendmail(from_email, recipient_list, msg.as_string())

        logger.info(f"邮件发送成功到: {email}")
        return Response({'message': '验证码已发送'}, status=200)
    
    except smtplib.SMTPException as e:
        if str(e) == "(-1, b'\\x00\\x00\\x00')":
            logger.warning(f"忽略特定的SMTP错误: {e}")
            return Response({'message': '验证码已发送'}, status=200)
        else:
            logger.error(f"发送邮件时发生其他SMTP错误: {str(e)}")
            return Response({'error': '发送邮件失败，请稍后重试'}, status=500)
    
    except Exception as e:
        logger.error(f"发送邮件时发生未知错误: {str(e)}")
        return Response({'error': '发送邮件失败，请稍后重试'}, status=500)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from .models import FirstLevelUser, FirstLevelUserInvite
from datetime import datetime

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    invite_code = request.data.get('invite_code')  # 获取邀请码

    # 验证表单字段是否存在
    if not username or not password or not email:
        return Response({'error': '用户名、密码和邮箱都是必填项'}, status=status.HTTP_400_BAD_REQUEST)

    # 检查用户名是否已被使用
    if User.objects.filter(username=username).exists():
        return Response({'error': '用户名已存在'}, status=status.HTTP_400_BAD_REQUEST)

    # 检查邮箱是否已被使用
    if User.objects.filter(email=email).exists():
        return Response({'error': '邮箱已被注册'}, status=status.HTTP_400_BAD_REQUEST)

    # 创建新用户
    user = User.objects.create(
        username=username,
        email=email,
        password=make_password(password),  # 密码加密
    )

    # 创建一级用户的相关信息
    first_level_user = FirstLevelUser.objects.create(
        user=user,
        expiration_date=datetime.now(),  # 设置默认到期时间
    )

    # 处理邀请码，记录邀请关系
    if invite_code:
        try:
            # 使用 invite_code 解析出 inviter 的 user_id
            inviter_user_id = force_str(urlsafe_base64_decode(invite_code))


            inviter = FirstLevelUser.objects.get(user_id=inviter_user_id)
            
            # 创建邀请关系
            FirstLevelUserInvite.objects.create(
                inviter=inviter,
                invitee=first_level_user
            )
        except (FirstLevelUser.DoesNotExist, ValueError):
            # 如果邀请码无效，继续完成注册，但不记录邀请关系
            pass

    return Response({'success': '注册成功'}, status=status.HTTP_201_CREATED)


# 邮箱验证码注册e

@api_view(['POST'])

def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)



# 上传订单s
import os
import pandas as pd
from django.conf import settings
from django.db import IntegrityError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_order(request):
    user = request.user
    logger.debug(f"User {user.username} is uploading an order")

    try:
        first_level_user = FirstLevelUser.objects.get(user=user)
        logger.debug(f"First level user: {first_level_user}")
    except FirstLevelUser.DoesNotExist:
        logger.error(f"First level user does not exist for user {user.username}")
        return Response({'error': '用户不是一级用户'}, status=status.HTTP_400_BAD_REQUEST)

    if 'file' not in request.FILES:
        logger.error("No file found in the request")
        return Response({'error': '未找到文件'}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES['file']
    file_path = os.path.join(settings.MEDIA_ROOT, file.name)

    # 确保媒体目录存在
    if not os.path.exists(settings.MEDIA_ROOT):
        os.makedirs(settings.MEDIA_ROOT)
        logger.debug(f"Created media directory at {settings.MEDIA_ROOT}")

    logger.debug(f"Saving file to {file_path}")

    with open(file_path, 'wb') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    logger.debug("File saved successfully")

    failed_orders = []  # 用于记录失败的订单编号
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file.name.endswith('.xls'):
            df = pd.read_excel(file_path, engine='xlrd')
        elif file.name.endswith('.xlsx'):
            df = pd.read_excel(file_path, engine='openpyxl')
        else:
            os.remove(file_path)
            logger.error("Unsupported file format")
            return Response({'error': '不支持的文件格式'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证文件内容
        expected_columns = {'口令单号', '金额', '活动店铺'}
        logger.debug(f"DataFrame columns: {df.columns}")  # 打印DataFrame的列
        if not expected_columns.issubset(df.columns):
            os.remove(file_path)
            logger.error("File missing necessary columns")
            return Response({'error': '文件缺少必要的列，请检查文件格式'}, status=status.HTTP_400_BAD_REQUEST)

        logger.debug(f"DataFrame loaded: {df.head()}")  # 打印前几行数据

        for index, row in df.iterrows():
            shop_name = row['活动店铺']
            try:
                shop = Shop.objects.get(name=shop_name, owner=first_level_user)
                logger.debug(f"Found shop: {shop.name}")
            except Shop.DoesNotExist:
                logger.error(f"Shop {shop_name} not found for user {user.username}")
                failed_orders.append(row['口令单号'])
                continue  # 跳过找不到对应店铺的订单
            
            amount = Decimal(row['金额'])
            if shop.commission_method == 'fixed':
                commission_amount = shop.fixed_commission
            elif shop.commission_method == 'percentage':
                commission_amount = amount * (shop.percentage_commission / 100)
            elif shop.commission_method == 'commission_and_principal':
                commission_amount = amount + shop.fixed_commission_with_principal
            else:
                commission_amount = 0

            try:
                Order.objects.create(
                    order_number=row['口令单号'],
                    amount=row['金额'],
                    commission_amount=commission_amount,
                    shop=shop,
                    first_level_user=first_level_user
                )
                logger.debug(f"Order created: {row['口令单号']}")
            except IntegrityError:
                logger.error(f"Order number {row['口令单号']} already exists")
                failed_orders.append(row['口令单号'])

        os.remove(file_path)  # 删除处理完的文件
        if failed_orders:
            logger.warning(f"Some orders failed: {failed_orders}")
            return Response({'success': '部分订单上传成功', 'failed_orders': failed_orders},
                            status=status.HTTP_207_MULTI_STATUS)
        logger.debug("All orders uploaded successfully")
        return Response({'success': '所有订单上传成功'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        if os.path.exists(file_path):
            os.remove(file_path)  # 确保文件在异常情况下也被删除
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 上传订单e
# 一级用户活动s
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import FirstLevelUser, Event

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_event(request):
    user = request.user
    first_level_user_user_id = request.query_params.get('first_level_user_user_id')

    try:
        if first_level_user_user_id:
            first_level_user = FirstLevelUser.objects.get(user_id=first_level_user_user_id)
        else:
            first_level_user = FirstLevelUser.objects.get(user=user)

        event = Event.objects.get(first_level_user=first_level_user)
        event_data = {
            'id': event.id,
            'title': event.title,
            'commandTitle': event.command_title,
            'commandDescription': event.command_description,
            'image': event.image,
        }
        return Response(event_data, status=status.HTTP_200_OK)
    except FirstLevelUser.DoesNotExist:
        return Response({'error': '一级用户不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Event.DoesNotExist:
        return Response({'error': '活动不存在'}, status=status.HTTP_404_NOT_FOUND)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def log_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '')
        logger.info(message)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)




import os
import uuid
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Event, FirstLevelUser
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_image(request):
    logger.debug("Received file upload request.")

    if 'file' not in request.FILES:
        logger.error("No file found in the request.")
        return Response({'error': '未找到文件'}, status=400)

    file = request.FILES['file']
    logger.debug(f"File received: {file.name}")
    user = request.user

    try:
        first_level_user = FirstLevelUser.objects.get(user=user)
        event, created = Event.objects.get_or_create(first_level_user=first_level_user)
    except FirstLevelUser.DoesNotExist:
        logger.error("First level user does not exist.")
        return Response({'error': '一级用户不存在'}, status=404)

    # 记录旧图片路径
    old_image_path = os.path.join(settings.MEDIA_ROOT, os.path.basename(event.image)) if event.image else None
    logger.debug(f"Old image path: {old_image_path}")

    # 生成唯一文件名
    ext = file.name.split('.')[-1]  # 获取文件扩展名
    unique_filename = f"{uuid.uuid4()}.{ext}"  # 使用UUID生成唯一文件名
    file_path = os.path.join(settings.MEDIA_ROOT, unique_filename)
    logger.debug(f"Saving file to {file_path}")

    try:
        with open(file_path, 'wb') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        return Response({'error': '文件保存失败'}, status=500)

    # 删除旧图片
    if old_image_path and os.path.exists(old_image_path) and old_image_path != file_path:
        logger.debug(f"Removing old image at {old_image_path}")
        try:
            os.remove(old_image_path)
            logger.debug(f"Old image {old_image_path} removed successfully.")
        except Exception as e:
            logger.error(f"Failed to remove old image: {e}")

    # 更新事件的图片路径，确保路径带有 `/media/` 前缀
    event.image = f'/media/{unique_filename}'
    event.save()

    # 返回完整的图片 URL
    file_url = f'/media/{unique_filename}'
    logger.debug(f"Returning file URL: {file_url}")

    return Response({'url': file_url}, status=200)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_event(request):
    logger.debug("Received save event request.")

    user = request.user
    try:
        first_level_user = FirstLevelUser.objects.get(user=user)
        data = request.data
        title = data.get('title', '返佣活动')
        image = data.get('image', '')
        command_title = data.get('commandTitle', '口令')
        command_description = data.get('commandDescription', '请输入口令')

        event, created = Event.objects.update_or_create(
            first_level_user=first_level_user,
            defaults={
                'title': title,
                'image': image,
                'command_title': command_title,
                'command_description': command_description
            }
        )

        logger.debug(f"Event saved with ID: {event.id}")
        return Response({'id': event.id}, status=200)
    except FirstLevelUser.DoesNotExist:
        logger.error("First level user does not exist.")
        return Response({'error': '一级用户不存在'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_image(request):
    url = request.data.get('url')
    if not url:
        return Response({'error': '未提供要删除的图片URL'}, status=400)

    image_path = os.path.join(settings.MEDIA_ROOT, os.path.basename(url))
    if os.path.exists(image_path):
        os.remove(image_path)
        return Response({'success': '图片已删除'}, status=200)
    else:
        return Response({'error': '图片不存在'}, status=404)




from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Event
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_event_link(request):
    user = request.user
    try:
        event_id = request.data.get('id')
        event = Event.objects.get(id=event_id)

        # 使用 urlsafe_base64_encode 对 user_id 和 event_id 分别进行加密
        encoded_user_id = urlsafe_base64_encode(force_bytes(event.first_level_user.user.id))
        encoded_event_id = urlsafe_base64_encode(force_bytes(event.id))

        # 构建活动链接，将 user_id 和 event_id 分别传递，保持原来的样式
        event_link = f"https://dingdanbao.top/wechat-auth?user_id={encoded_user_id}&event_id={encoded_event_id}"
        logger.debug(f"生成的活动链接: {event_link}")

        event.link = event_link
        event.save()

        return Response({'event_link': event_link}, status=200)
    except Event.DoesNotExist:
        logger.error(f"活动不存在，event_id: {event_id}")
        return Response({'error': '活动不存在'}, status=404)


# 一级用户活动e
# 创建活动 二级用户登录 提交订单编号 s
import logging
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import requests
logger = logging.getLogger(__name__)

def get_wechat_auth_data(code):
    appid = settings.WECHAT_APP_ID  # 在 settings.py 中配置真实的 AppID
    secret = settings.WECHAT_APP_SECRET  # 在 settings.py 中配置真实的 AppSecret
    
    # 请求微信服务器，使用 code 换取 access_token 和 openid
    token_url = f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={appid}&secret={secret}&code={code}&grant_type=authorization_code"
    response = requests.get(token_url)
    return response.json()

def get_wechat_user_info(access_token, openid):
    user_info_url = f"https://api.weixin.qq.com/sns/userinfo?access_token={access_token}&openid={openid}&lang=zh_CN"
    response = requests.get(user_info_url)
    return response.json()

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import redirect
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import FirstLevelUser, SecondLevelUser, FirstLevelUserSecondLevelUser, Event
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def wechat_auth(request):
    # 打印所有的 GET 参数用于调试
    logger.debug(f"收到的 GET 参数: {request.GET}")

    # 获取微信传回的 code、user_id 和 event_id 参数
    code = request.GET.get('code')
    encoded_user_id = request.GET.get('state')
    encoded_event_id = request.GET.get('event_id')

    # 检查是否缺少必要的参数
    if not code or not encoded_user_id:
        logger.error("缺少必要的参数: code 或 user_id")
        return Response({'error': '缺少必要的参数'}, status=400)

    try:
        # 解码 user_id
        user_id = force_str(urlsafe_base64_decode(encoded_user_id))
        logger.debug(f"解码后的 user_id: {user_id}")
    except (ValueError, TypeError, Exception) as e:
        logger.error(f"无效的 user_id 解码: {e}")
        return Response({'error': '无效的 user_id'}, status=400)

    # event_id 是可选的
    if encoded_event_id:
        try:
            event_id = force_str(urlsafe_base64_decode(encoded_event_id))
            logger.debug(f"解码后的 event_id: {event_id}")
        except (ValueError, TypeError, Exception) as e:
            logger.error(f"无效的 event_id 解码: {e}")
            return Response({'error': '无效的 event_id'}, status=400)
    else:
        event_id = None

    # 通过 user_id 查找 FirstLevelUser
    try:
        first_level_user = FirstLevelUser.objects.get(user_id=user_id)
    except FirstLevelUser.DoesNotExist:
        logger.error(f"一级用户不存在，user_id: {user_id}")
        return Response({'error': '一级用户不存在'}, status=404)

    # 使用 code 获取微信 access_token 和 openid
    auth_data = get_wechat_auth_data(code)
    if 'errcode' in auth_data:
        logger.error(f"微信授权失败，code: {code}, 错误: {auth_data}")
        return Response({'error': '微信授权失败'}, status=400)

    openid = auth_data.get('openid')
    access_token = auth_data.get('access_token')

    # 获取微信用户信息
    wechat_user_info = get_wechat_user_info(access_token, openid)

    # 获取并尝试修正编码的微信昵称
    raw_nickname = wechat_user_info.get('nickname', '')

    try:
        decoded_nickname = raw_nickname.encode('latin1').decode('utf-8')
        logger.debug(f"解码后的微信昵称: {decoded_nickname}")
    except UnicodeDecodeError:
        decoded_nickname = raw_nickname
        logger.warning(f"微信昵称解码失败，保留原始数据: {raw_nickname}")

    # 创建或获取二级用户
    wechat_user, created = User.objects.get_or_create(username=openid)
    second_level_user, second_level_user_created = SecondLevelUser.objects.get_or_create(user=wechat_user)

    # 保存微信昵称到数据库
    second_level_user.wechat_nickname = decoded_nickname
    second_level_user.save()

    # 建立一级用户和二级用户的关系
    FirstLevelUserSecondLevelUser.objects.get_or_create(first_level_user=first_level_user,
                                                        second_level_user=second_level_user)

    # 生成 JWT token
    refresh = RefreshToken.for_user(wechat_user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    # 重定向到前端页面，传递 token 和用户信息
    response = redirect(
        f"https://dingdanbao.top/claim-order?suser_id={second_level_user.user.id}&fuser_id={first_level_user.user.id}&user_id={encoded_user_id}&token={access_token}&refresh_token={refresh_token}")
    response['Authorization'] = f'Bearer {access_token}'
    response['Refresh-Token'] = refresh_token

    return response


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import PendingOrderRequest, Order, Blacklist, SecondLevelUser, FirstLevelUser
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def claim_order(request):
    order_number = request.data.get('order_number')
    first_level_user_user_id = request.data.get('first_level_user_user_id')
    user = request.user
    logger.debug(f"Received order number: {order_number}, User ID: {user.id}, First Level User ID: {first_level_user_user_id}")

    try:
        # 获取二级用户
        second_level_user = SecondLevelUser.objects.get(user=user)
        logger.debug(f"SecondLevelUser found: {second_level_user}")
    except SecondLevelUser.DoesNotExist:
        logger.error(f"SecondLevelUser does not exist for user_id={user.id}")
        return Response({'error': '二级用户不存在'}, status=404)

    try:
        # 获取一级用户
        first_level_user = FirstLevelUser.objects.get(user__id=first_level_user_user_id)
        logger.debug(f"FirstLevelUser found: {first_level_user}")
    except FirstLevelUser.DoesNotExist:
        logger.error(f"FirstLevelUser does not exist for user_id={first_level_user_user_id}")
        return Response({'error': '一级用户不存在'}, status=404)

    # 检查该二级用户是否在一级用户的黑名单中
    if Blacklist.objects.filter(first_level_user=first_level_user, second_level_user=second_level_user).exists():
        logger.warning(f"Second level user {second_level_user.user.username} is blacklisted by {first_level_user.user.username}")
        return Response({'error': '暂时无法提交订单，请联系店主处理'}, status=403)

    # 检查订单号是否已存在于 PendingOrderRequest 表中
    if PendingOrderRequest.objects.filter(order_number=order_number).exists():
        logger.error(f"Order number {order_number} already exists in PendingOrderRequest table")
        return Response({'error': '订单已经提交，请等待处理'}, status=400)

    # 检查订单号是否已存在于 Order 表中，并且状态为 distributed
    try:
        order = Order.objects.get(order_number=order_number)
        if order.status == 'distributed':
            logger.error(f"Order number {order_number} has already been processed")
            return Response({'error': '订单已经处理过，不需要再提交'}, status=400)
        elif order.status == 'pending':
            # 订单存在并且状态为 pending，可以提交到 PendingOrderRequest 表中
            logger.debug(f"Order number {order_number} is in pending status")
            pass
    except Order.DoesNotExist:
        # 订单不存在于 Order 表中，可以提交到 PendingOrderRequest 表中
        logger.debug(f"Order number {order_number} does not exist in Order table, proceeding with PendingOrderRequest creation")
        pass

    try:
        # 创建待审核订单请求
        logger.debug(f"Creating PendingOrderRequest for order number: {order_number}, FirstLevelUser: {first_level_user.user.username}")
        PendingOrderRequest.objects.create(
            order_number=order_number, 
            second_level_user=second_level_user, 
            first_level_user=first_level_user
        )
        logger.debug(f"Pending order request created for order number: {order_number}")
        return Response({'success': '订单已提交，待处理'}, status=201)
    except Exception as e:
        logger.error(f"Error creating pending order request: {e}", exc_info=True)
        return Response({'error': '订单提交失败'}, status=500)

# 创建活动 二级用户登录 提交订单编号 e


# 添加店铺s
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_shop(request):
    user = request.user
    logger.debug(f"User {user.username} is adding a shop with request data: {request.data}")

    try:
        first_level_user = FirstLevelUser.objects.get(user=user)
    except FirstLevelUser.DoesNotExist:
        logger.error(f"First level user does not exist for user {user.username}")
        return Response({'error': '一级用户不存在'}, status=status.HTTP_404_NOT_FOUND)

    shop_name = request.data.get('name')
    if not shop_name:
        logger.error("Shop name is required")
        return Response({'error': '店铺名称是必需的'}, status=status.HTTP_400_BAD_REQUEST)

    # 获取当前一级用户的店铺数量
    shop_count = Shop.objects.filter(owner=first_level_user).count()

    # 如果店铺数量小于等于 3，则将新店铺的审核状态设为已审核
    if shop_count < 3:
        approved_status = True
    else:
        approved_status = False

    # 创建店铺
    shop = Shop.objects.create(name=shop_name, owner=first_level_user, approved=approved_status)
    
    logger.debug(f"Shop {shop_name} created with approval status {approved_status}")
    return Response({'success': f'店铺已创建, 审核状态: {"已审核" if approved_status else "待审核"}'}, status=status.HTTP_201_CREATED)


# 添加店铺e


# 二级用户管理 s
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_second_level_users(request):
    try:
        first_level_user = FirstLevelUser.objects.get(user=request.user)
        second_level_users = SecondLevelUser.objects.filter(
            firstlevelusersecondleveluser__first_level_user=first_level_user
        )

        serialized_users = SecondLevelUserSerializer(second_level_users, many=True).data

        for user in serialized_users:
            user_shops = Shop.objects.filter(secondlevelusershop__second_level_user_id=user['id'])
            user['shops'] = ShopSerializer(user_shops, many=True).data

            # 查询该用户是否被当前一级用户拉黑
            is_blacklisted = Blacklist.objects.filter(
                first_level_user=first_level_user,
                second_level_user_id=user['id']
            ).exists()
            user['is_blacklisted'] = is_blacklisted

        return Response(serialized_users, status=200)

    except FirstLevelUser.DoesNotExist:
        return Response({'error': '一级用户不存在'}, status=404)
    except Exception as e:
        return Response({'error': f'获取二级用户列表失败: {str(e)}'}, status=500)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def manage_user_shop(request):
    second_level_user_id = request.data.get('second_level_user_id')
    shop_id = request.data.get('shop_id')
    action = request.data.get('action')

    try:
        second_level_user = SecondLevelUser.objects.get(id=second_level_user_id)
        shop = Shop.objects.get(id=shop_id)

        if action == 'add':
            second_level_user.shops.add(shop)
        elif action == 'remove':
            second_level_user.shops.remove(shop)
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': 'Association updated successfully'}, status=status.HTTP_200_OK)
    except SecondLevelUser.DoesNotExist:
        return Response({'error': 'SecondLevelUser not found'}, status=status.HTTP_404_NOT_FOUND)
    except Shop.DoesNotExist:
        return Response({'error': 'Shop not found'}, status=status.HTTP_404_NOT_FOUND)

# 二级用户管理 e

# 二级用户待审核订单s


# 修改后的 get_pending_orders 函数
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.db.models import Count
from .models import PendingOrderRequest, Blacklist


from django.db.models import Count
from .models import PendingOrderRequest, Blacklist

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_orders(request):
    user = request.user
    try:
        first_level_user = FirstLevelUser.objects.get(user=user)
    except FirstLevelUser.DoesNotExist:
        return Response({'error': '一级用户不存在'}, status=status.HTTP_404_NOT_FOUND)

    pending_orders = PendingOrderRequest.objects.filter(first_level_user=first_level_user).order_by('-add_time')
    serialized_orders = []

    # 获取每个订单的 second_level_user 相关黑名单信息
    for order in pending_orders:
        blacklist_entries = Blacklist.objects.filter(second_level_user=order.second_level_user)
        total_blacklist_count = blacklist_entries.count()
        reasons = {}

        # 统计不同原因的拉黑次数，并获取中文显示
        for entry in blacklist_entries:
            reason_display = entry.get_reason_display()  # 使用中文显示
            reasons[reason_display] = reasons.get(reason_display, 0) + 1

        # 为每个订单添加黑名单信息
        serialized_order = PendingOrderRequestSerializer(order).data
        serialized_order['blacklist_info'] = {
            'total_blacklist_count': total_blacklist_count,
            'reasons': reasons
        }
        serialized_orders.append(serialized_order)

    return Response(serialized_orders)



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_pending_order(request, pk):
    user = request.user
    try:
        first_level_user = FirstLevelUser.objects.get(user=user)
    except FirstLevelUser.DoesNotExist:
        return Response({'error': '一级用户不存在'}, status=status.HTTP_404_NOT_FOUND)

    pending_order = get_object_or_404(PendingOrderRequest, pk=pk, first_level_user=first_level_user)
    pending_order.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_delete_pending_orders(request):
    user = request.user
    ids = request.data.get('ids', [])
    try:
        first_level_user = FirstLevelUser.objects.get(user=user)
    except FirstLevelUser.DoesNotExist:
        return Response({'error': '一级用户不存在'}, status=status.HTTP_404_NOT_FOUND)

    PendingOrderRequest.objects.filter(id__in=ids, first_level_user=first_level_user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# 二级用户待审核订单e

# 资金记录s
from rest_framework import viewsets
from .models import BalanceChangeRecord
from .serializers import BalanceChangeRecordSerializer

class BalanceChangeRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BalanceChangeRecord.objects.all()
    serializer_class = BalanceChangeRecordSerializer
    def get_queryset(self):
        # 如果需要根据当前用户过滤资金记录
        user = self.request.user
        return BalanceChangeRecord.objects.filter(user=user)
# 资金记录e

# 批量删除一级用户订单s
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Order, FirstLevelUser
from django.shortcuts import get_object_or_404

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_delete_orders(request):
    user = request.user
    ids = request.data.get('ids', [])
    try:
        first_level_user = FirstLevelUser.objects.get(user=user)
    except FirstLevelUser.DoesNotExist:
        return Response({'error': '一级用户不存在'}, status=status.HTTP_404_NOT_FOUND)

    orders_to_delete = Order.objects.filter(id__in=ids, first_level_user=first_level_user, status='pending')
    orders_to_delete.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)

# 批量删除一级用户订单e

# 有原密码修改密码s
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')

    if not user.check_password(current_password):
        return Response({'error': '当前密码不正确'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()
    update_session_auth_hash(request, user)  # 确保用户会话在更改密码后保持有效

    return Response({'success': '密码修改成功'}, status=status.HTTP_200_OK)

# 有原密码修改密码e
from rest_framework.decorators import api_view
from .models import SecondLevelUser

@api_view(['GET'])
def user_info(request):
    user = request.user
    try:
        second_level_user = SecondLevelUser.objects.get(user=user)
        return Response({"username": second_level_user.user.username,
                         "level": "second",})
    except SecondLevelUser.DoesNotExist:
        # 如果是一级用户
        try:
            first_level_user = FirstLevelUser.objects.get(user=user)
            is_expired = first_level_user.expiration_date and first_level_user.expiration_date < timezone.now()
            print(f"User: {first_level_user.user.username}, Expiration Date: {first_level_user.expiration_date}, Is Expired: {is_expired}")
            return Response({"username": first_level_user.user.username, "level": "first",
                             "expiryDate": first_level_user.expiration_date.strftime('%Y-%m-%d'),
                             "balance": first_level_user.balance,"is_expired": is_expired,})
        except FirstLevelUser.DoesNotExist:
            return Response({"error": "User not found in either level"}, status=400)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import PendingOrderRequest, Order
from .serializers import PendingOrderRequestSerializer, OrderSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_order_requests(request):
    user = request.user
    second_level_user = user.secondleveluser
    first_level_user_user_id = request.query_params.get('first_level_user_user_id')

    print(f"Received first_level_user_user_id: {first_level_user_user_id}")

    if not first_level_user_user_id:
        print("Missing first_level_user_user_id parameter")
        return Response({"error": "Missing first_level_user_user_id parameter"}, status=400)

    first_level_user = second_level_user.first_level_users.filter(user__id=first_level_user_user_id).first()
    if not first_level_user:
        print("Invalid first level user")
        return Response({"error": "Invalid first level user"}, status=400)

    print(f"Filtering pending requests for second_level_user: {second_level_user.user.username} and first_level_user: {first_level_user.user.username}")
    pending_requests = PendingOrderRequest.objects.filter(second_level_user=second_level_user, first_level_user=first_level_user).order_by('-add_time')
    serializer = PendingOrderRequestSerializer(pending_requests, many=True)
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_completed_orders(request):
    user = request.user
    second_level_user = user.secondleveluser
    first_level_user_user_id = request.query_params.get('first_level_user_user_id')

    print(f"Received first_level_user_user_id: {first_level_user_user_id}")

    if not first_level_user_user_id:
        print("Missing first_level_user_user_id parameter")
        return Response({"error": "Missing first_level_user_user_id parameter"}, status=400)

    print(f"Filtering completed orders for second_level_user: {second_level_user.user.username} and first_level_user_user_id: {first_level_user_user_id}")
    completed_orders = Order.objects.filter(tijiao=second_level_user.user.username,
                                            first_level_user__user__id=first_level_user_user_id, status='distributed').order_by('-update_time')

    print(f"Found completed orders: {completed_orders.count()}")
    # for order in completed_orders:
    #     print(f"Order: {order.order_number}, Amount: {order.amount}, Status: {order.status}")

    serializer = OrderSerializer(completed_orders, many=True)
    return Response(serializer.data)


# 一级用户首页展示s

from rest_framework.decorators import api_view
from .models import SecondLevelUser, FirstLevelUser, Order
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum

@api_view(['GET'])
def get_dashboard_stats(request):
    user = request.user
    try:
        first_level_user = FirstLevelUser.objects.get(user=user)
    except FirstLevelUser.DoesNotExist:
        return Response({"error": "First level user not found."}, status=status.HTTP_404_NOT_FOUND)

    today = datetime.now().date()
    start_time = make_aware(datetime.combine(today, datetime.min.time()))
    end_time = make_aware(datetime.combine(today, datetime.max.time()))

    # 昨日时间范围
    yesterday = today - timedelta(days=1)
    start_yesterday = make_aware(datetime.combine(yesterday, datetime.min.time()))
    end_yesterday = make_aware(datetime.combine(yesterday, datetime.max.time()))

    # 本月开始时间
    first_day_of_month = today.replace(day=1)
    start_month = make_aware(datetime.combine(first_day_of_month, datetime.min.time()))

    new_members_today = SecondLevelUser.objects.filter(
        first_level_users=first_level_user,
        add_time__range=(start_time, end_time)
    ).count()

    total_members = SecondLevelUser.objects.filter(
        first_level_users=first_level_user
    ).count()

    total_refunds_today = Order.objects.filter(
        status='distributed',
        first_level_user=first_level_user,
        add_time__range=(start_time, end_time)
    ).aggregate(total=Sum('commission_amount'))['total'] or 0

    total_refunds_yesterday = Order.objects.filter(
        status='distributed',
        first_level_user=first_level_user,
        add_time__range=(start_yesterday, end_yesterday)
    ).aggregate(total=Sum('commission_amount'))['total'] or 0

    pending_orders_count = PendingOrderRequest.objects.filter(
        first_level_user=first_level_user
    ).count()

    approved_orders_this_month = Order.objects.filter(
        status='distributed',
        first_level_user=first_level_user,
        add_time__range=(start_month, end_time)
    ).count()

    unassigned_members_count = SecondLevelUser.objects.filter(
        first_level_users=first_level_user,
        shops__isnull=True
    ).count()

    unassigned_members_percentage = (unassigned_members_count / total_members * 100) if total_members > 0 else 0

    stats = {
        "new_members_today": new_members_today,
        "total_refunds_today": total_refunds_today,
        "total_refunds_yesterday": total_refunds_yesterday,
        "pending_orders_count": pending_orders_count,
        "approved_orders_this_month": approved_orders_this_month,
        "unassigned_members_count": unassigned_members_count,
        "unassigned_members_percentage": unassigned_members_percentage,  # 添加未分配会员的百分比
        "total_members": total_members,
    }

    return Response(stats)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.utils.timezone import localtime
from dateutil.relativedelta import relativedelta
from .models import FirstLevelUser, Order, Shop
import logging

# 设置日志记录器
logger = logging.getLogger(__name__)

from django.utils.timezone import now
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Order, Shop
from dateutil.relativedelta import relativedelta

@api_view(['GET'])
def get_monthly_refunds(request):
    user = request.user
    first_level_user = FirstLevelUser.objects.get(user=user)
    
    # 获取最近6个月
    current_date = now()
    start_date = current_date - relativedelta(months=6)
    
    refunds = Order.objects.filter(
        status='distributed',
        first_level_user=first_level_user,
        add_time__gte=start_date
    ).annotate(
        month=TruncMonth('add_time')
    ).values('month', 'shop__name').annotate(
        total_refund=Sum('commission_amount')
    ).order_by('month', 'shop__name')
    
    data = {}
    for refund in refunds:
        month = refund['month'].strftime('%Y-%m')
        shop_name = refund['shop__name']
        if month not in data:
            data[month] = {}
        data[month][shop_name] = refund['total_refund'] or 0

    # 按月份格式化输出
    months = [(current_date - relativedelta(months=i)).strftime('%Y-%m') for i in range(6)]
    all_shops = Shop.objects.filter(owner=first_level_user).values_list('name', flat=True)
    
    result = {
        "months": months,
        "data": {shop: [data.get(month, {}).get(shop, 0) for month in months] for shop in all_shops}
    }
    
    return Response(result)


from django.db.models.functions import TruncDay
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Sum

@api_view(['GET'])
def get_daily_refunds(request):
    user = request.user
    first_level_user = FirstLevelUser.objects.get(user=user)

    current_date = now()
    start_date = current_date - timedelta(days=30)

    refunds = Order.objects.filter(
        status='distributed',
        first_level_user=first_level_user,
        add_time__gte=start_date
    ).annotate(
        day=TruncDay('add_time')
    ).values('day', 'shop__name').annotate(
        total_refund=Sum('commission_amount')
    ).order_by('day', 'shop__name')

    data = {}
    for refund in refunds:
        day = refund['day'].strftime('%Y-%m-%d')
        shop_name = refund['shop__name']
        if day not in data:
            data[day] = {}
        data[day][shop_name] = refund['total_refund'] or 0

    days = [(current_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]
    all_shops = Shop.objects.filter(owner=first_level_user).values_list('name', flat=True)

    result = {
        "days": days,
        "data": {shop: [data.get(day, {}).get(shop, 0) for day in days] for shop in all_shops}
    }

    return Response(result)


@api_view(['GET'])
def get_user_refund_ranking(request):
    user = request.user
    try:
        first_level_user = FirstLevelUser.objects.get(user=user)
        logger.debug(f"Found first level user: {first_level_user}")
    except FirstLevelUser.DoesNotExist:
        logger.error("First level user not found")
        return Response({"error": "First level user not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        # 获取已分配佣金的二级用户及其佣金总额
        refunds = (
            Order.objects.filter(status='distributed', first_level_user=first_level_user)
            .values('tijiao')
            .annotate(total_refund=Sum('commission_amount'))  # 使用佣金金额
            .order_by('-total_refund')  # 按照佣金总额降序排序
        )
        logger.debug(f"Refund data: {refunds}")

        # 将 None 的总额转换为 0
        refund_dict = {refund['tijiao']: refund['total_refund'] or 0 for refund in refunds}
        logger.debug(f"Refund dict: {refund_dict}")

        # 获取所有二级用户
        second_level_users = SecondLevelUser.objects.filter(first_level_users=first_level_user)
        logger.debug(f"Second level users: {second_level_users}")

        # 创建用户排名，先按总金额排序，再分配排名
        ranking = sorted(
            [
                {
                    "username": second_level_user.user.username,
                    "total_refund": refund_dict.get(second_level_user.user.username, 0)
                }
                for second_level_user in second_level_users
            ],
            key=lambda x: x['total_refund'],  # 根据佣金金额排序
            reverse=True  # 按降序排序
        )

        # 为排序后的用户分配正确的排名
        for idx, user in enumerate(ranking):
            user["rank"] = idx + 1  # 根据排序后的顺序生成排名

        logger.debug(f"Ranking data: {ranking}")

        # 返回前 20 个用户
        ranking = ranking[:20]

        return Response(ranking)
    except Exception as e:
        logger.error(f"Error in get_user_refund_ranking: {e}")
        return Response({"error": "Data processing error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 一级用户首页展示e



# agiso自动获取订单s

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.conf import settings


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def authorize_auto_fetch(request):
    try:
        shop_id = request.data.get('shop_id')
        if not shop_id:
            return Response({'error': '缺少店铺ID'}, status=400)

        print(f"Shop ID received: {shop_id}")

        try:
            first_level_user = FirstLevelUser.objects.get(user=request.user)
            print(f"First Level User: {first_level_user.user.username}")
        except FirstLevelUser.DoesNotExist:
            print("First Level User does not exist")
            return Response({'error': '一级用户不存在'}, status=404)

        try:
            shop = Shop.objects.get(id=shop_id, owner=first_level_user)
            print(f"Shop found: {shop.name} (ID: {shop.id})")
        except Shop.DoesNotExist:
            print("Shop does not exist or does not belong to this user")
            return Response({'error': '店铺不存在或没有权限访问'}, status=404)

        print(f"Shop auto_fetch_enabled status: {shop.auto_fetch_enabled}")

        if not shop.auto_fetch_enabled:
            app_id = settings.AGISO_APP_ID
            state = shop.id
            auth_url = f"https://alds.agiso.com/authorize.aspx?appId={app_id}&state={state}&redirect_uri=https:dingdanbaob.top/agiso-callback/"
            # auth_url = f"https://alds.agiso.com/authorize.aspx?appId={app_id}&state={state}&redirect_uri=http://192.168.1.8:8000/api/agiso-callback/"
            print(f"Generated Auth URL: {auth_url}")
            return Response({'auth_url': auth_url}, status=status.HTTP_200_OK)

        return Response({'error': '自动获取订单已开启'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Shop, FirstLevelUser
import requests

@api_view(['GET'])
@permission_classes([AllowAny])
def agiso_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')

    if not code or not state:
        return Response({'error': '缺少必要的参数'}, status=400)

    try:
        # 获取店铺信息
        shop = Shop.objects.get(id=state)
        first_level_user = shop.owner

        # 使用 code 和 appSecret 换取 AccessToken
        app_id = settings.AGISO_APP_ID
        app_secret = settings.AGISO_APP_SECRET
        token_url = f"https://alds.agiso.com/auth/token?code={code}&appId={app_id}&secret={app_secret}&state={state}"
        response = requests.get(token_url)
        token_data = response.json()

        if token_data.get('IsSuccess'):
            user_nick = token_data['Data'].get('UserNick')
            access_token = token_data['Data']['Token']
            # 将 access_token 保存到 Shop 模型中
            shop.tbnick = user_nick
            shop.access_token = access_token
            shop.auto_fetch_enabled = True
            shop.save()

            # 重定向到前端
            return redirect('https://dingdanbao.top/shops')
        else:
            return Response({'error': '获取AccessToken失败'}, status=400)

    except Shop.DoesNotExist:
        return Response({'error': '店铺不存在'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

import json
from .models import Order
import logging
logger = logging.getLogger(__name__)


from django.conf import settings
import hashlib
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from .models import Shop, Order
import json

logger = logging.getLogger(__name__)

def validate_sign(query_params, provided_sign, json_data):
    app_secret = settings.AGISO_APP_SECRET

    timestamp = query_params.get('timestamp')
    if not timestamp:
        logger.error("Timestamp missing")
        return False

    sign_str = f"{app_secret}json{json_data}timestamp{timestamp}{app_secret}"
    logger.debug(f"String to be signed: {sign_str}")

    calculated_sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
    
    logger.debug(f"Calculated Sign: {calculated_sign}")
    logger.debug(f"Provided Sign: {provided_sign}")

    return calculated_sign.lower() == provided_sign.lower()

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from .signals import calculate_commission
import logging
from .models import Order, Shop
import json
from decimal import Decimal
logger = logging.getLogger(__name__)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def receive_order_push(request):
    json_data = request.data.get('json')  # 获取传递的 JSON 数据
    provided_sign = request.GET.get('sign')  # 获取签名参数

    # 如果json_data不存在，记录并返回错误
    if not json_data:
        logger.error("No JSON data received")
        return Response({'error': 'No JSON data received'}, status=status.HTTP_400_BAD_REQUEST)

    # 调用签名验证逻辑
    if not validate_sign(request.GET, provided_sign, json_data):
        logger.error(f"Signature validation failed for provided_sign: {provided_sign}")
        return Response({'error': '签名验证失败'}, status=status.HTTP_403_FORBIDDEN)

    try:
        # 将 JSON 数据转为 Python 字典
        order_data = json.loads(json_data)
        logger.debug(f"Order data received: {order_data}")

        seller_nick = order_data.get('SellerNick')  # 获取 SellerNick（卖家昵称）
        buyer_open_uid = order_data.get('BuyerOpenUid')

        if not seller_nick:
            logger.error("SellerNick is missing from order data")
            return Response({'error': 'SellerNick is missing'}, status=status.HTTP_400_BAD_REQUEST)

        # 使用卖家昵称 seller_nick 查找店铺（使用 tbnick 字段）
        shop = Shop.objects.get(tbnick__iexact=seller_nick)
        commission_amount = calculate_commission(shop, Decimal(order_data['Payment']))

        # 创建订单记录
        order = Order.objects.create(
            shop=shop,
            order_number=order_data['Tid'],
            amount=order_data['Payment'],
            commission_amount=commission_amount,
            buyer_open_uid=buyer_open_uid,
            first_level_user=shop.owner
        )

        logger.debug(f"Order {order.order_number} created for BuyerOpenUid {buyer_open_uid}")
        return Response({'success': '订单已保存'}, status=status.HTTP_201_CREATED)

    except json.JSONDecodeError:
        logger.error("Failed to decode JSON")
        return Response({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)
    except Shop.DoesNotExist:
        logger.error(f"Shop with SellerNick {seller_nick} does not exist in tbnick field")
        return Response({'error': '店铺不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# agiso自动获取订单e



# 取消agiso自动获取订单s
import requests
import hashlib
import time
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Shop
import logging
logger = logging.getLogger(__name__)


import requests
import time
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def agiso_cancel_authorization(shop):
    logger = logging.getLogger(__name__)
    logger.debug(f"Function agiso_cancel_authorization called for shop ID: {shop.id}")
    logger.debug(f"Received shop access_token: {shop.access_token}")
    logger.debug(f"Received shop auto_fetch_enabled: {shop.auto_fetch_enabled}")
    logger.debug("Function agiso_cancel_authorization called")  # 检查函数是否被调用
    access_token = shop.access_token
    if not access_token:
        logger.error("Access token is missing for shop.")
        return {'error': 'Access token missing'}

    url = "http://gw.api.agiso.com/alds/Sys/TokenDelete"
    headers = {'Authorization': f'Bearer {access_token}', 'ApiVersion': '1'}
    timestamp = int(time.time())
    data = {'timestamp': str(timestamp)}
    sign = generate_sign(data, settings.AGISO_APP_SECRET)
    data["sign"] = sign

    logger.debug(f"Headers: {headers}")
    logger.debug(f"Data: {data}")

    try:
        response = requests.post(url, headers=headers, data=data)
        logger.debug(f"API Response status: {response.status_code}")
        logger.debug(f"API Response content: {response.content}")
        if response.status_code == 200:
            api_response = response.json()
            if api_response.get('IsSuccess'):
                shop.auto_fetch_enabled = False
                shop.access_token = None
                shop.tbnick = None
                shop.save()
                return {'success': 'Authorization cancelled successfully'}
            else:
                error_msg = api_response.get('Error_Msg', 'Failed to cancel authorization')
                logger.error(f"Failed to cancel authorization: {error_msg}")
                return {'error': error_msg}
        else:
            logger.error(f"Failed to connect to API: {response.status_code}")
            return {'error': 'Failed to connect to API'}
    except Exception as e:
        logger.error(f"Error during API call: {str(e)}")
        return {'error': str(e)}




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_auto_fetch(request):
    user = request.user
    shop_id = request.data.get('shop_id')
    try:
        shop = Shop.objects.get(id=shop_id, owner__user=user)
        if not shop.auto_fetch_enabled:
            return Response({'error': '自动获取订单未开启'}, status=400)

        result = agiso_cancel_authorization(shop)
        if 'success' in result:
            return Response(result, status=200)
        else:
            return Response(result, status=400)

    except Shop.DoesNotExist:
        return Response({'error': '店铺不存在或无权访问'}, status=404)
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        return Response({'error': str(e)}, status=500)



def generate_sign(params, app_secret):
    """
    生成签名
    """
    sorted_keys = sorted(params.keys())
    query = app_secret + ''.join(f"{key}{params[key]}" for key in sorted_keys) + app_secret
    md5_hash = hashlib.md5(query.encode('utf-8')).hexdigest()
    return md5_hash

import time
import requests
from django.conf import settings
from .models import Shop
import logging

logger = logging.getLogger(__name__)

def auto_cancel_fetch_for_expired_user(first_level_user):
    """
    针对已到期的一级用户，自动取消其所有店铺的自动获取订单功能。
    """
    try:
        # 获取该用户的所有启用自动获取订单的店铺
        shops = Shop.objects.filter(owner=first_level_user, auto_fetch_enabled=True)

        if not shops.exists():
            logger.info(f"用户 {first_level_user.user.username} 没有启用自动获取订单的店铺。")
            return {"success": "没有需要取消自动获取订单的店铺"}

        for shop in shops:
            access_token = shop.access_token
            if not access_token:
                logger.error(f"店铺 {shop.name} 的授权令牌丢失，无法取消授权。")
                continue

            # 调用Agiso平台接口取消授权
            url = "http://gw.api.agiso.com/alds/Sys/TokenDelete"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'ApiVersion': '1'
            }

            # 添加公共参数
            timestamp = int(time.time())
            data = {
                'timestamp': str(timestamp),
            }

            # 生成签名
            sign = generate_sign(data, settings.AGISO_APP_SECRET)
            data["sign"] = sign

            # 发起POST请求
            response = requests.post(url, headers=headers, data=data)

            if response.status_code == 200:
                try:
                    api_response = response.json()
                    if api_response.get('IsSuccess'):
                        shop.auto_fetch_enabled = False
                        shop.access_token = None
                        shop.tbnick = None  # 清空淘宝昵称
                        shop.save()
                        logger.info(f"店铺 {shop.name} 的自动获取订单功能已成功取消。")
                    else:
                        logger.error(f"店铺 {shop.name} 取消授权失败: {api_response.get('Error_Msg')}")
                except ValueError:
                    logger.error(f"无法解析店铺 {shop.name} 的取消授权响应。")
            else:
                logger.error(f"取消店铺 {shop.name} 的授权失败，状态码: {response.status_code}")

        return {"success": "已处理所有店铺的自动获取订单取消操作"}

    except Exception as e:
        logger.error(f"自动取消授权时发生错误: {str(e)}")
        return {"error": str(e)}

# 取消agiso自动获取订单e

# 忘记密码重置s

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
import ssl
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import logging

logger = logging.getLogger(__name__)

from smtplib import SMTPException
import socket

@api_view(['POST'])
@permission_classes([AllowAny])
def send_reset_link(request):
    username = request.data.get('username')
    email = request.data.get('email')

    try:
        user = User.objects.get(username=username, email=email)
    except User.DoesNotExist:
        return Response({'error': '用户名和邮箱不匹配'}, status=400)

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_link = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"

    subject = '密码重置请求'
    message = f'请点击以下链接来重置您的密码：\n{reset_link}\n\n如果您没有请求此操作，请忽略此邮件。'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    try:
        # 配置 SSL 上下文
        ssl_context = ssl.create_default_context(cafile='/etc/ssl/certs/ca-certificates.crt')

        # 创建邮件消息
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = from_email
        msg['To'] = ','.join(recipient_list)

        # 发送邮件
        with smtplib.SMTP_SSL('smtp.qq.com', 465, context=ssl_context) as server:
            server.login(from_email, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(from_email, recipient_list, msg.as_string())

        return Response({'message': '密码重置链接已发送到您的邮箱'}, status=200)

    except smtplib.SMTPException as e:
        if str(e) == "(-1, b'\\x00\\x00\\x00')":
            # 忽略特定异常并继续返回成功
            logger.warning(f"忽略特定异常: {e}, 继续发送成功提示")
            return Response({'message': '密码重置链接已发送到您的邮箱'}, status=200)
        else:
            logger.error(f"发送邮件时发生SMTP错误: {e}")
            return Response({'error': '发送邮件失败，请稍后重试'}, status=500)

    except socket.gaierror as e:
        logger.error(f"网络问题，无法发送邮件: {e}")
        return Response({'error': '发送邮件失败，网络问题'}, status=500)

    except Exception as e:
        logger.error(f"发送邮件时发生未知错误: {e}")
        return Response({'error': '发送邮件失败，请稍后重试'}, status=500)




from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        return Response({'error': '无效的链接'}, status=400)

    if not default_token_generator.check_token(user, token):
        return Response({'error': '令牌无效或已过期'}, status=400)

    new_password = request.data.get('new_password')
    if not new_password:
        return Response({'error': '新密码是必需的'}, status=400)

    user.set_password(new_password)
    user.save()

    return Response({'message': '密码已重置成功'}, status=200)




# 忘记密码重置e




# 后端生成微信授权 URL 的接口s
from django.conf import settings
from django.http import JsonResponse
import urllib.parse

def generate_wechat_auth_link(request):
    user_id = request.GET.get('user_id')

    if not user_id:
        return JsonResponse({'error': 'Missing user_id'}, status=400)

    appid = settings.WECHAT_APP_ID  # 使用真实的公众号 AppID
    redirect_uri = urllib.parse.quote('https://www.dingdanbaob.top/wechat-auth')  # 与微信公众平台配置一致
    wechat_auth_url = (
        f"https://open.weixin.qq.com/connect/oauth2/authorize?appid={appid}"
        f"&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_userinfo&state={user_id}#wechat_redirect"
    )

    return JsonResponse({'wechat_auth_url': wechat_auth_url})

# 后端生成微信授权 URL 的接口e


# 处理微信支付通知的视图s
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def wechat_pay_notify(request):
    # 微信支付的通知处理逻辑
    return JsonResponse({'code': 'SUCCESS'})

# 处理微信支付通知的视图e


#佣金相关代码s
from django.views.decorators.http import require_POST

@csrf_exempt
@require_POST
def save_commission_method(request):
    try:
        data = json.loads(request.body)
        shop_id = data.get('shop_id')
        commission_method = data.get('commission_method')
        fixed_commission = data.get('fixed_commission', None)
        percentage_commission = data.get('percentage_commission', None)
        fixed_commission_with_principal = data.get('fixed_commission_with_principal', None)

        # 获取店铺
        shop = Shop.objects.get(id=shop_id)

        # 根据佣金方式清除不相关的字段
        if commission_method == 'fixed':
            percentage_commission = None
            fixed_commission_with_principal = None
        elif commission_method == 'percentage':
            fixed_commission = None
            fixed_commission_with_principal = None
        elif commission_method == 'commission_and_principal':
            fixed_commission = None
            percentage_commission = None

        # 更新店铺的佣金信息
        shop.commission_method = commission_method
        shop.fixed_commission = fixed_commission
        shop.percentage_commission = percentage_commission
        shop.fixed_commission_with_principal = fixed_commission_with_principal
        shop.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"保存佣金设置失败: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

#佣金相关代码e


#计算用户关联店铺会员总数s
from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import SecondLevelUser

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_shop_counts(request):
    try:
        # 获取每个二级用户关联的店铺数量
        users_shop_counts = SecondLevelUser.objects.annotate(total_shops=Count('shops')).values('user__username', 'total_shops')
        
        # 返回统计数据
        return Response(list(users_shop_counts), status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


#计算用户关联店铺会员总数e


#拉黑取消用户s

from .models import Blacklist, SecondLevelUser, FirstLevelUser,ActivationCode
from .serializers import BlacklistSerializer

# 拉黑用户
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Blacklist, FirstLevelUser, SecondLevelUser, UserAssociation
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_blacklist(request):
    try:
        second_level_user_id = request.data.get('second_level_user_id')
        reason = request.data.get('reason')

        if not second_level_user_id or not reason:
            logger.warning("Missing second_level_user_id or reason")
            return Response({'error': 'Missing second_level_user_id or reason'}, status=status.HTTP_400_BAD_REQUEST)

        first_level_user = FirstLevelUser.objects.get(user=request.user)
        second_level_user = SecondLevelUser.objects.get(id=second_level_user_id)

        logger.info(f"Processing blacklist for SecondLevelUser: {second_level_user.user.username}")

        # 已处理的用户和buyer_open_uid，用于防止重复处理
        processed_users = set()
        processed_buyers = set()

        # 递归函数，拉黑所有关联的用户和buyer_open_uid
        def recursive_blacklist(second_user, buyer_uid=None):
            # 如果 second_user 和 buyer_open_uid 组合已处理，跳过
            if (second_user.id, buyer_uid) in processed_users:
                return
            processed_users.add((second_user.id, buyer_uid))

            # 如果没有 buyer_uid，查找关联表获取所有buyer_open_uid
            if not buyer_uid:
                associations = UserAssociation.objects.filter(second_level_user=second_user)
                if associations.exists():
                    buyer_uid = associations.first().buyer_open_uid

            # 检查是否有相同的 first_level_user, second_level_user 和 buyer_open_uid 记录
            if not Blacklist.objects.filter(first_level_user=first_level_user, second_level_user=second_user, buyer_open_uid=buyer_uid).exists():
                # 创建黑名单条目
                Blacklist.objects.create(
                    first_level_user=first_level_user,
                    second_level_user=second_user,
                    reason=reason,
                    buyer_open_uid=buyer_uid
                )
                logger.info(f"Blacklisted SecondLevelUser: {second_user.user.username} with buyer_open_uid: {buyer_uid}")
            else:
                logger.info(f"Skipped: SecondLevelUser: {second_user.user.username} already blacklisted with buyer_open_uid: {buyer_uid}")

            # 获取与 second_user 关联的所有 buyer_open_uid
            related_associations = UserAssociation.objects.filter(second_level_user=second_user).values_list('buyer_open_uid', flat=True).distinct()
            for buyer_open_uid in related_associations:
                if buyer_open_uid not in processed_buyers:
                    processed_buyers.add(buyer_open_uid)

                    # 获取此 buyer_open_uid 关联的所有 second_level_user
                    related_second_users = UserAssociation.objects.filter(buyer_open_uid=buyer_open_uid).values_list('second_level_user', flat=True).distinct()

                    # 递归处理与buyer_open_uid相关的其他用户
                    for related_second_user_id in related_second_users:
                        related_second_user = SecondLevelUser.objects.get(id=related_second_user_id)
                        recursive_blacklist(related_second_user, buyer_open_uid)
                else:
                    logger.info(f"Buyer_open_uid: {buyer_open_uid} already processed for SecondLevelUser: {second_user.user.username}")

        # 开始处理当前的二级用户和关联用户
        recursive_blacklist(second_level_user)

        logger.info("Blacklist process completed successfully.")
        return Response({'success': 'Blacklist processed successfully'}, status=status.HTTP_200_OK)

    except FirstLevelUser.DoesNotExist:
        logger.error("First level user not found")
        return Response({'error': 'First level user not found'}, status=status.HTTP_404_NOT_FOUND)

    except SecondLevelUser.DoesNotExist:
        logger.error("Second level user not found")
        return Response({'error': 'Second level user not found'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 取消拉黑
import logging
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_from_blacklist(request):
    try:
        second_level_user_id = request.data.get('second_level_user_id')

        if not second_level_user_id:
            logger.warning("Missing second_level_user_id in request")
            return Response({'error': 'Missing second_level_user_id'}, status=status.HTTP_400_BAD_REQUEST)

        first_level_user = FirstLevelUser.objects.get(user=request.user)
        second_level_user = SecondLevelUser.objects.get(id=second_level_user_id)

        def recursively_remove_blacklist(second_user):
            logger.info(f"Removing blacklist for SecondLevelUser: {second_user.user.username}")
            
            Blacklist.objects.filter(first_level_user=first_level_user, second_level_user=second_user).delete()

            related_associations = UserAssociation.objects.filter(second_level_user=second_user)
            for association in related_associations:
                buyer_open_uid = association.buyer_open_uid

                Blacklist.objects.filter(first_level_user=first_level_user, buyer_open_uid=buyer_open_uid).delete()

                related_second_level_users = UserAssociation.objects.filter(buyer_open_uid=buyer_open_uid).exclude(second_level_user=second_user)

                for related_user in related_second_level_users:
                    if Blacklist.objects.filter(first_level_user=first_level_user, second_level_user=related_user.second_level_user).exists():
                        recursively_remove_blacklist(related_user.second_level_user)

        with transaction.atomic():
            recursively_remove_blacklist(second_level_user)

        logger.info(f"Successfully removed blacklist for user {second_level_user_id} and related users")
        return Response({'success': '用户和相关用户的拉黑状态已取消'}, status=status.HTTP_200_OK)

    except FirstLevelUser.DoesNotExist:
        logger.error(f"FirstLevelUser does not exist for user {request.user}")
        return Response({'error': '一级用户不存在'}, status=status.HTTP_404_NOT_FOUND)
    except SecondLevelUser.DoesNotExist:
        logger.error(f"SecondLevelUser with ID {second_level_user_id} does not exist")
        return Response({'error': '二级用户不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Failed to remove blacklist: {str(e)}")
        return Response({'error': f'取消拉黑操作失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 获取黑名单s

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

class BlacklistPagination(PageNumberPagination):
    page_size = 10  # 每页显示10条数据
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_blacklist(request):
    try:
        first_level_user = FirstLevelUser.objects.get(user=request.user)
        blacklists = Blacklist.objects.filter(first_level_user=first_level_user)

        paginator = BlacklistPagination()
        result_page = paginator.paginate_queryset(blacklists, request)
        
        blacklist_data = []
        for blacklist in result_page:
            user_data = {
                'second_level_user_id': blacklist.second_level_user.id,
                'second_level_user_username': blacklist.second_level_user.user.username,
                'reason_display': blacklist.get_reason_display(),
                'buyer_open_uid': blacklist.buyer_open_uid,
                'related_blacklisted_users': []
            }

            related_users = UserAssociation.objects.filter(buyer_open_uid__in=UserAssociation.objects.filter(
                second_level_user=blacklist.second_level_user).values('buyer_open_uid'))

            related_usernames = set()
            for related_user in related_users:
                if related_user.second_level_user != blacklist.second_level_user:
                    related_blacklist_entry = Blacklist.objects.filter(
                        first_level_user=first_level_user,
                        second_level_user=related_user.second_level_user
                    ).first()

                    if related_blacklist_entry:
                        related_username = related_blacklist_entry.second_level_user.user.username
                        if related_username not in related_usernames:
                            related_usernames.add(related_username)
                            user_data['related_blacklisted_users'].append({
                                'username': related_username,
                                'reason': related_blacklist_entry.get_reason_display()
                            })

            blacklist_data.append(user_data)

        return paginator.get_paginated_response(blacklist_data)

    except FirstLevelUser.DoesNotExist:
        return Response({'error': '一级用户不存在'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


#拉黑取消用户e


# 激活码相关S
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def use_activation_code(request):
    code = request.data.get('code')
    action_type = request.data.get('action_type')  # 区分是“续费”还是“充值”
    user = request.user

    try:
        # 查找未使用的激活码
        activation_code = ActivationCode.objects.get(code=code, is_used=False)
    except ActivationCode.DoesNotExist:
        return Response({"error": "无效或已使用的激活码"}, status=400)

    try:
        # 查找用户的一级用户记录
        first_level_user = FirstLevelUser.objects.get(user=user)
    except FirstLevelUser.DoesNotExist:
        return Response({"error": "用户不是一级用户"}, status=400)

    # 检查激活码的用途是否与操作匹配
    if action_type != activation_code.type:
        return Response({"error": f"该激活码仅用于 {activation_code.get_type_display()}，请检查操作类型"}, status=400)

    if action_type == 'renew':  # 使用激活码续费
        # 延长用户的到期时间
        if first_level_user.expiration_date:
            first_level_user.expiration_date += timedelta(days=int(activation_code.value))
        else:
            first_level_user.expiration_date = timezone.now() + timedelta(days=int(activation_code.value))
        first_level_user.save()
        message = f"账户到期时间已延长{int(activation_code.value)}天"

        # 处理邀请奖励
        try:
            invite_record = FirstLevelUserInvite.objects.get(invitee=first_level_user, rewarded=False)
            invite_record.rewarded = True
            invite_record.rewarded_at = timezone.now()  # 记录当前的赠送时间
            invite_record.save()

            # 给邀请者（inviter）增加额外的30天到期时间
            inviter = invite_record.inviter
            if inviter.expiration_date:
                inviter.expiration_date += timedelta(days=30)
            else:
                inviter.expiration_date = timezone.now() + timedelta(days=30)
            inviter.save()

        except FirstLevelUserInvite.DoesNotExist:
            # 如果没有找到邀请记录，继续执行其他逻辑
            pass

    elif action_type == 'recharge':  # 使用激活码充值
        # 为用户增加余额
        first_level_user.balance += activation_code.value
        first_level_user.save()
        message = f"账户余额已增加{activation_code.value}元"

        # 记录一条充值资金记录
        BalanceChangeRecord.objects.create(
            user=user,
            balance=first_level_user.balance,
            change_type='入账',
            change_amount=activation_code.value,
            time=timezone.now(),
            order_number=activation_code.code  # 使用激活码作为单号
        )

    # 标记激活码为已使用
    activation_code.is_used = True
    activation_code.used_by = user
    activation_code.used_at = timezone.now()
    activation_code.save()

    return Response({"success": message})

# 激活码相关e








# 邀请一级用户s
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import FirstLevelUser, FirstLevelUserInvite

# 获取邀请信息的接口，返回当前用户的邀请链接和统计信息
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.timezone import localtime
from .models import FirstLevelUser, FirstLevelUserInvite

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_invite_info(request):
    user = request.user
    try:
        inviter = FirstLevelUser.objects.get(user=user)
        invitees = FirstLevelUserInvite.objects.filter(inviter=inviter).select_related('invitee')
        invitee_info = []
        for invitee in invitees:
            invitee_user = invitee.invitee.user
            invitee_info.append({
                'username': invitee_user.username,
                'created_at': localtime(invitee.created_at).strftime('%Y-%m-%d %H:%M:%S'),  # 格式化时间为字符串
                'is_rewarded': invitee.rewarded,
                'rewarded_at': localtime(invitee.rewarded_at).strftime('%Y-%m-%d %H:%M:%S') if invitee.rewarded_at else None,  # 赠送时间
            })
        return Response({'invitees': invitee_info})
    except FirstLevelUser.DoesNotExist:
        return Response({"error": "用户不是一级用户"}, status=400)

# 生成用户的邀请链接
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from .models import FirstLevelUser

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_invite_link(request):
    user = request.user

    try:
        first_level_user = FirstLevelUser.objects.get(user=user)
    except FirstLevelUser.DoesNotExist:
        return Response({"error": "用户不是一级用户"}, status=400)

    # 使用 user.id 生成邀请码
    invite_code = urlsafe_base64_encode(force_bytes(user.id))
    invite_link = f"{settings.FRONTEND_URL}/register/?invite_code={invite_code}"

    return Response({"invite_url": invite_link})

# 邀请一级用户e


