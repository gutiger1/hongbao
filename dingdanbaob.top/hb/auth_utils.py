import time
from OpenSSL import crypto
from django.conf import settings
import base64
import logging

# 设置日志记录器
logger = logging.getLogger(__name__)

# 生成随机字符串作为 nonce_str
def generate_nonce_str(length=32):
    return ''.join([str(x) for x in range(length)])

# 生成签名
def generate_signature(message, private_key_path):
    try:
        with open(private_key_path, 'rb') as key_file:
            private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, key_file.read())
        
        # 生成签名 (二进制格式)
        signature = crypto.sign(private_key, message.encode('utf-8'), 'sha256')

        # 使用 base64 编码签名，便于传输
        return base64.b64encode(signature).decode('utf-8')
    except Exception as e:
        logger.error(f"生成签名失败: {e}")
        raise

# 生成授权头
def generate_authorization_header(method, url, body):
    try:
        mch_id = settings.WECHAT_PAY['mch_id']
        serial_no = settings.WECHAT_PAY['serial_no']
        timestamp = str(int(time.time()))
        nonce_str = generate_nonce_str()

        # 组合待签名的信息
        message = f"{method}\n{url}\n{timestamp}\n{nonce_str}\n{body}\n"

        # 使用商户私钥签名
        private_key_path = settings.WECHAT_PAY['key_path']
        signature = generate_signature(message, private_key_path)

        # 构造 Authorization 头
        authorization = (
            f'WECHATPAY2-SHA256-RSA2048 mchid="{mch_id}",'
            f'serial_no="{serial_no}",timestamp="{timestamp}",'
            f'nonce_str="{nonce_str}",signature="{signature}"'
        )

        return authorization
    except Exception as e:
        logger.error(f"生成授权头失败: {e}")
        raise
