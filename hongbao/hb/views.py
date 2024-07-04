from django.db.models import Count
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Order, SecondLevelUser, PendingOrderRequest, FirstLevelUser


# def claim_order(request):
#     if request.method == 'POST':
#         order_number = request.POST.get('order_number')
#         user = request.user
#         second_level_user = SecondLevelUser.objects.get(user=user)
#
#         try:
#             order = Order.objects.get(order_number=order_number)
#
#             if order.status == 'distributed':
#                 return JsonResponse({'status': 'error', 'message': '订单已经发放，不再发放金额'})
#
#             if order.shop not in second_level_user.shops.all():
#                 return JsonResponse({'status': 'error', 'message': '不是该店铺会员，请联系店长处理'})
#
#             if order.status == 'pending':
#                 order.second_level_user = second_level_user
#                 order.mark_as_distributed()
#                 # 这里可以添加代码将订单金额发送到二级用户的微信
#                 return JsonResponse({'status': 'success', 'amount': order.amount})
#         except Order.DoesNotExist:
#             # 如果订单不存在，则存储该订单请求
#             pending_order_request, created = PendingOrderRequest.objects.get_or_create(
#                 order_number=order_number,
#                 second_level_user=second_level_user
#             )
#             return JsonResponse({'status': 'error', 'message': '后台数据暂未更新，数据已经提交，请等待后台自动处理。'})
#     return render(request, 'claim_order.html')
# 获取一级用户信息新增代码段

from rest_framework.decorators import api_view, permission_classes  # 确保导入 api_view 和 permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import FirstLevelUser
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    user = request.user
    try:
        first_level_user = FirstLevelUser.objects.get(user=user)
        user_data = {
            "expiryDate": first_level_user.expiration_date,  # 假设用户的到期日期存储在 expiration_date 字段中
            "balance": first_level_user.balance,
        }
        return Response(user_data, status=status.HTTP_200_OK)
    except FirstLevelUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
from rest_framework import viewsets, permissions, status
from .models import Order, SecondLevelUser, PendingOrderRequest,Shop
from .serializers import OrderSerializer, SecondLevelUserSerializer, PendingOrderRequestSerializer,ShopSerializer

# hb/views.py
from rest_framework import viewsets, permissions
from .models import Order, Shop, FirstLevelUser
from .serializers import OrderSerializer, ShopSerializer

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return Order.objects.none()
        try:
            first_level_user = FirstLevelUser.objects.get(user=user)
        except FirstLevelUser.DoesNotExist:
            return Order.objects.none()
        return Order.objects.filter(first_level_user=first_level_user)

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
        data = [{
            'name': shop.name,
            'second_level_users_count': shop.second_level_users_count
        } for shop in queryset]
        return Response(data)





class SecondLevelUserViewSet(viewsets.ModelViewSet):
    queryset = SecondLevelUser.objects.all()
    serializer_class = SecondLevelUserSerializer

class PendingOrderRequestViewSet(viewsets.ModelViewSet):
    queryset = PendingOrderRequest.objects.all()
    serializer_class = PendingOrderRequestSerializer

# 新增
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging
from .models import FirstLevelUser
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    logger.debug(f"Received data: {request.data}")
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': '用户名和密码是必需的'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': '用户名已存在'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.create_user(username=username, password=password)
        # 创建 FirstLevelUser 记录
        expiration_date = datetime.now() + timedelta(days=365)  # 设置默认到期时间为一年后
        FirstLevelUser.objects.create(user=user, expiration_date=expiration_date)
        return Response({'success': '注册成功'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
# def login_view(request):
#     logger.debug(f"Received data: {request.data}")
#
#     username = request.data.get('username')
#     password = request.data.get('password')
#
#     if user := authenticate(username=username, password=password):
#         login(request, user)
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({'token': token.key})
#
#     return Response({'error': '用户名或密码错误'}, status=400)
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
import logging
import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from django.conf import settings
from .models import Order, FirstLevelUser, Shop
from django.db import IntegrityError

logger = logging.getLogger(__name__)


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
        expected_columns = {'订单编号', '订单金额', '所属店铺'}
        if not expected_columns.issubset(df.columns):
            os.remove(file_path)
            logger.error("File missing necessary columns")
            return Response({'error': '文件缺少必要的列，请检查文件格式'}, status=status.HTTP_400_BAD_REQUEST)

        logger.debug(f"DataFrame loaded: {df.head()}")  # 打印前几行数据

        for index, row in df.iterrows():
            shop_name = row['所属店铺']
            try:
                shop = Shop.objects.get(name=shop_name, owner=first_level_user)
                logger.debug(f"Found shop: {shop.name}")
            except Shop.DoesNotExist:
                logger.error(f"Shop {shop_name} not found for user {user.username}")
                failed_orders.append(row['订单编号'])
                continue  # 跳过找不到对应店铺的订单

            try:
                Order.objects.create(
                    order_number=row['订单编号'],
                    amount=row['订单金额'],
                    shop=shop,
                    first_level_user=first_level_user
                )
                logger.debug(f"Order created: {row['订单编号']}")
            except IntegrityError:
                logger.error(f"Order number {row['订单编号']} already exists")
                failed_orders.append(row['订单编号'])

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

# 创建活动 二级用户登录 提交订单编号 s

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_event_link(request):
    user = request.user
    try:
        first_level_user = FirstLevelUser.objects.get(user=user)
        event_link = f"http://192.168.1.3:5173/wechat-auth?user_id={first_level_user.user.id}"
        return Response({'event_link': event_link}, status=status.HTTP_200_OK)
    except FirstLevelUser.DoesNotExist:
        return Response({'error': '一级用户不存在'}, status=status.HTTP_404_NOT_FOUND)



from rest_framework.permissions import AllowAny, IsAuthenticated
import logging

logger = logging.getLogger(__name__)

from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import FirstLevelUser, SecondLevelUser, User
import requests
import logging

logger = logging.getLogger(__name__)

def get_wechat_auth_data(code):
    url = f"https://api.weixin.qq.com/sns/oauth2/access_token?appid=wxb5b1322aaf1cd850&secret=fdd43dad5612449c5cfb945e48b36b9b&code={code}&grant_type=authorization_code"
    response = requests.get(url)
    return response.json()

@api_view(['GET'])
@permission_classes([AllowAny])
def wechat_auth(request):
    code = request.GET.get('code')
    user_id = request.GET.get('state')  # 获取 state 中的 user_id
    logger.debug(f"Received code: {code}, user_id: {user_id}")

    if not code or not user_id:
        logger.error(f"Missing parameters: code={code}, user_id={user_id}")
        return Response({'error': '缺少必要的参数'}, status=400)

    auth_data = get_wechat_auth_data(code)
    logger.debug(f"auth_data: {auth_data}")

    if 'errcode' in auth_data:
        logger.error(f"WeChat auth error: {auth_data}")
        return Response({'error': '微信授权失败'}, status=400)

    openid = auth_data.get('openid')
    logger.debug(f"openid: {openid}")

    try:
        first_level_user = FirstLevelUser.objects.get(user_id=user_id)
        logger.debug(f"FirstLevelUser found: {first_level_user}")
    except FirstLevelUser.DoesNotExist:
        logger.error(f"FirstLevelUser does not exist for user_id={user_id}")
        return Response({'error': '一级用户不存在'}, status=404)

    # 创建或获取二级用户
    wechat_user, created = User.objects.get_or_create(username=openid)
    if created:
        second_level_user = SecondLevelUser.objects.create(user=wechat_user)
    else:
        second_level_user = SecondLevelUser.objects.get(user=wechat_user)
    logger.debug(f"SecondLevelUser: {second_level_user}")

    # 生成 JWT Token
    refresh = RefreshToken.for_user(wechat_user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    # 返回前端地址和 token
    response = redirect(f"http://192.168.1.3:5173/claim-order?user_id={second_level_user.user.id}&token={access_token}&refresh_token={refresh_token}")
    response['Authorization'] = f'Bearer {access_token}'
    response['Refresh-Token'] = refresh_token

    return response






@api_view(['POST'])
@permission_classes([IsAuthenticated])
def claim_order(request):
    order_number = request.data.get('order_number')
    user = request.user
    logger.debug(f"Received order number: {order_number}, User ID: {user.id}")

    try:
        second_level_user = SecondLevelUser.objects.get(user=user)
        logger.debug(f"SecondLevelUser found: {second_level_user}")
    except SecondLevelUser.DoesNotExist:
        logger.error(f"SecondLevelUser does not exist for user_id={user.id}")
        return Response({'error': '二级用户不存在'}, status=404)

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
            pass
    except Order.DoesNotExist:
        # 订单不存在于 Order 表中，可以提交到 PendingOrderRequest 表中
        pass

    try:
        PendingOrderRequest.objects.create(order_number=order_number, second_level_user=second_level_user)
        logger.debug(f"Pending order request created for order number: {order_number}")
        return Response({'success': '订单已提交，待处理'}, status=201)
    except Exception as e:
        logger.error(f"Error creating pending order request: {e}", exc_info=True)
        return Response({'error': '订单提交失败'}, status=500)

# 创建活动 二级用户登录 提交订单编号 e
