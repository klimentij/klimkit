from __future__ import annotations

from typing import Protocol
from urllib import parse, request


class TelegramNotificationConfig(Protocol):
    telegram_enabled: bool
    telegram_bot_token: str
    telegram_chat_id: str


def send_telegram_notification(config: TelegramNotificationConfig, text: str) -> bool:
    if not config.telegram_enabled or not config.telegram_bot_token or not config.telegram_chat_id:
        return False
    endpoint = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"
    payload = parse.urlencode(
        {
            "chat_id": config.telegram_chat_id,
            "text": text,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    req = request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with request.urlopen(req, timeout=10) as response:
        response.read()
    return True
