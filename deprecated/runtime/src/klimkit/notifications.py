from __future__ import annotations

from typing import Protocol
from urllib import parse, request


class TelegramNotificationConfig(Protocol):
    telegram_enabled: bool
    telegram_bot_token: str
    telegram_chat_id: str


def build_direct_code_server_url(dns_name: str, folder: str) -> str:
    host = str(dns_name or "").strip().rstrip(".")
    target = str(folder or "").strip()
    if not host or not target or "/" in host or ":" in host:
        return ""
    return f"https://{host}/?folder={parse.quote(target, safe='/')}"


def send_telegram_notification(config: TelegramNotificationConfig, text: str) -> bool:
    return send_telegram_message(config, text)


def send_telegram_message(
    config: TelegramNotificationConfig,
    text: str,
    *,
    parse_mode: str = "",
) -> bool:
    if not config.telegram_enabled or not config.telegram_bot_token or not config.telegram_chat_id:
        return False
    endpoint = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"
    payload_fields = {
        "chat_id": config.telegram_chat_id,
        "text": text,
        "disable_web_page_preview": "true",
    }
    if parse_mode:
        payload_fields["parse_mode"] = parse_mode
    payload = parse.urlencode(payload_fields).encode("utf-8")
    req = request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with request.urlopen(req, timeout=10) as response:
        response.read()
    return True
