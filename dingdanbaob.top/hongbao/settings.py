"""
Django settings for hongbao project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-dq50!4ds1t)#5&s_i)l*pcsqj@_z)90+%v(r1bd1$x7*(w1c+9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['dingdanbaob.top','192.168.158.138', 'localhost', '127.0.0.1','192.168.1.8','192.168.1.3','testserver', 'www.dingdanbaob.top']
CSRF_TRUSTED_ORIGINS = ['https://dingdanbaob.top', 'https://www.dingdanbaob.top']

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  # 启用分页默认每页显示10条数据
}



# Application definition

INSTALLED_APPS = [
    'django_celery_beat',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'hb.apps.HbConfig',

]
# 注册用户新增
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hongbao.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hongbao.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hongbao',
        'USER': 'hongbao',
        'PASSWORD': '1314521tian',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci';",
        },
    }
}





# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'
USE_TZ = True
import os
os.environ['TZ'] = 'Asia/Shanghai'

USE_I18N = True



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS_ALLOWED_ORIGINS = [
#     "http://192.168.1.3:5173",  # 添加前端开发服务器的地址
#     "http://192.168.30.1:5173",  # 添加前端开发服务器的地址
#     "http://192.168.158.1:5173",  # 添加前端开发服务器的地址
#     "http://192.168.158.138:8000",  # 如果需要其他地址也可以添加
# ]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True




LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',  # 添加时间戳的格式
            'datefmt': '%Y-%m-%d %H:%M:%S',  # 设置时间格式
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/www/wwwroot/dingdanbaob.top/log/debug.log',  # 改成你希望的路径
            'formatter': 'verbose',  # 使用 verbose 格式
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',  # 使用 verbose 格式
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'DEBUG',
    },
}



import os

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'staticfiles')]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

AGISO_APP_ID = '2024081247100215821'
AGISO_APP_SECRET = 'uw657twb4man46u27sa85y2ampesmbyv'

# 下面是测试微信公众号信息s
WECHAT_APP_ID = 'wxb5b1322aaf1cd850'
WECHAT_APP_SECRET = 'fdd43dad5612449c5cfb945e48b36b9b'
# 下面是测试微信公众号信息e
# WECHAT_APP_ID = 'wxadb6a050e99b3fe8'
# WECHAT_APP_SECRET = '2325a9d61031cc8edf2d93b3f361e5e3'


WECHAT_PAY = {
    'mch_id': '1685081744',  # 商户号
    'api_key': '1314521tian1314521tian1314521tia',  # APIv3密钥
    'appid': 'wxadb6a050e99b3fe8',  # 商户APPID
    'cert_path': os.path.join(BASE_DIR, 'certs/apiclient_cert.pem'),  # 商户证书路径
    'key_path': os.path.join(BASE_DIR, 'certs/apiclient_key.pem'),  # 商户私钥路径
    'serial_no': '7030736BBD387A0B0156E47DD8F0C0F33E08E45C',  # APIv3证书序列号
    'notify_url': 'https://dingdanbaob.top/notify/',  # 微信支付结果通知的回调地址
}

# 发送邮箱验证码所需s
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'  # QQ邮箱的SMTP服务器地址
EMAIL_PORT = 465  # QQ邮箱SMTP服务器端口（使用TLS加密）
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True  # 是否使用TLS加密
EMAIL_HOST_USER = '1500133824@qq.com'  # 你的QQ邮箱地址
EMAIL_HOST_PASSWORD = 'ouhjchhhzpzzffeh'  # 你的QQ邮箱授权码
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER  # 默认发件人邮箱地址


# 发送邮箱验证码所需e

FRONTEND_URL = 'https://dingdanbao.top'
# FRONTEND_URL = 'http://192.168.1.3:5173'


# 配置一级用户过期后自动取消agiso获取订单s

from datetime import timedelta

# Celery Broker 和 Backend 配置
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Celery 时区和时区感知设置
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = False

# Celery 任务调度配置
CELERY_BEAT_SCHEDULE = {
    'check_expired_users': {
        'task': 'hb.tasks.check_expired_users',
        'schedule': timedelta(minutes=10000),  # 每X分钟执行一次
    },
}


# 配置一级用户过期后自动取消agiso获取订单e


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # 设置 access token 有效期为 60 分钟（可以自定义）
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),  # 设置 refresh token 有效期为 7 天（可以自定义）
    'ROTATE_REFRESH_TOKENS': True,  # 刷新时会生成新的 refresh token
    'BLACKLIST_AFTER_ROTATION': True,  # 启用黑名单策略，以防止旧的 refresh token 使用
    'ALGORITHM': 'HS256',  # 默认算法为 HS256，可以调整为其他支持的加密算法
    'SIGNING_KEY': SECRET_KEY,  # 签名密钥，使用 Django 的 SECRET_KEY
}
