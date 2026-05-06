import time
import hmac
import hashlib
import base64
import logging
import httpx

logger = logging.getLogger(__name__)


async def send_feishu_message(
    webhook_url: str,
    content: dict,
    secret: str | None = None,
) -> None:
    """发送飞书 Webhook 消息"""
    payload = _build_payload(content, secret)

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(webhook_url, json=payload)
        response.raise_for_status()

        result = response.json()
        if result.get("code") != 0:
            raise Exception(f"飞书发送失败: {result.get('msg', '未知错误')}")

    logger.info("飞书消息发送成功")


def _build_payload(content: dict, secret: str | None = None) -> dict:
    """构建飞书消息体"""
    payload = {}

    # 签名验证
    if secret:
        timestamp = str(int(time.time()))
        string_to_sign = f"{timestamp}\n{secret}"
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        sign = base64.b64encode(hmac_code).decode("utf-8")
        payload["timestamp"] = timestamp
        payload["sign"] = sign

    # 构建富文本卡片
    title = content.get("title", "AI测试用例平台通知")
    text = content.get("text", "")
    link = content.get("link", "")

    payload["msg_type"] = "interactive"
    payload["card"] = {
        "header": {
            "title": {"tag": "plain_text", "content": title},
            "template": "blue",
        },
        "elements": [
            {
                "tag": "div",
                "text": {"tag": "lark_md", "content": text},
            },
        ],
    }

    if link:
        payload["card"]["elements"].append({
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "查看详情"},
                    "url": link,
                    "type": "primary",
                }
            ],
        })

    return payload


async def test_webhook(webhook_url: str, secret: str | None = None) -> bool:
    """测试飞书 Webhook 连接"""
    try:
        await send_feishu_message(
            webhook_url,
            {"title": "连接测试", "text": "飞书 Webhook 连接成功！"},
            secret,
        )
        return True
    except Exception as e:
        logger.error(f"飞书 Webhook 测试失败: {e}")
        raise
