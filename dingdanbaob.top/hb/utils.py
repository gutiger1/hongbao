import requests
import json
import logging
from django.conf import settings
from .auth_utils import generate_authorization_header, generate_nonce_str

logger = logging.getLogger(__name__)

# 调用微信支付API进行转账
def transfer_to_wechat_v3(openid, amount, desc, partner_trade_no):
    url = "/v3/transfer/batches"
    full_url = f"https://api.mch.weixin.qq.com{url}"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "",
    }

    # 构建请求体
    request_data = {
        "appid": settings.WECHAT_PAY['appid'],
        "out_batch_no": partner_trade_no,
        "batch_name": "佣金转账",
        "batch_remark": desc,
        "total_amount": amount,
        "total_num": 1,
        "transfer_detail_list": [
            {
                "out_detail_no": partner_trade_no,
                "transfer_amount": amount,
                "transfer_remark": desc,
                "openid": openid,
            }
        ]
    }

    body = json.dumps(request_data)

    try:
        # 生成授权头
        headers['Authorization'] = generate_authorization_header("POST", url, body)

        logger.debug(f"发送请求到微信支付: {body}")
        response = requests.post(full_url, headers=headers, data=body)
        result = response.json()
        
        if response.status_code == 200 and result.get("code") is None:
            logger.debug(f"转账成功，响应: {result}")
            # 返回 result 中的 batch_id
            return {"status": "success", "batch_id": result.get("batch_id")}
        else:
            logger.error(f"转账失败: {result}")
            return {"status": "fail", "error_msg": result}
    except Exception as e:
        logger.error(f"转账请求失败: {e}")
        return {"status": "fail", "error_msg": str(e)}
