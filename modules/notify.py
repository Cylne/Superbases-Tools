from __future__ import annotations
import requests
from .config import AppConfig

def notify(cfg: AppConfig, message: str) -> None:
    if not cfg.telegram_bot_token or not cfg.telegram_chat_id: return
    try:
        response = requests.post(f"https://api.telegram.org/bot{cfg.telegram_bot_token}/sendMessage", json={"chat_id": cfg.telegram_chat_id, "text": message}, timeout=15); response.raise_for_status()
    except requests.RequestException: return
