#!/usr/bin/env python3
"""
send_telegram.py

Sends digest.png to a Telegram chat via the Bot API, with a caption
that links to the live GitHub Pages URL.

Required environment variables:
  TELEGRAM_BOT_TOKEN   Bot token from @BotFather
  TELEGRAM_CHAT_ID     Target chat/channel/group ID
  PAGE_URL             Live GitHub Pages URL for the digest

Run:
  python scripts/send_telegram.py
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
IMAGE_PATH = REPO_ROOT / "digest.png"
IST = ZoneInfo("Asia/Kolkata")


def get_required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        print(f"ERROR: required environment variable {name} is not set.", file=sys.stderr)
        sys.exit(1)
    return value


def main():
    bot_token = get_required_env("TELEGRAM_BOT_TOKEN")
    chat_id = get_required_env("TELEGRAM_CHAT_ID")
    page_url = get_required_env("PAGE_URL")

    if not IMAGE_PATH.exists():
        print(f"ERROR: {IMAGE_PATH} not found. Run scripts/screenshot.py first.", file=sys.stderr)
        sys.exit(1)

    now_ist = datetime.now(IST)
    caption = (
        f"📰 Daily News Digest — {now_ist.strftime('%d %B %Y')}\n\n"
        f"🔗 View the live page: {page_url}"
    )

    api_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

    with open(IMAGE_PATH, "rb") as image_file:
        response = requests.post(
            api_url,
            data={"chat_id": chat_id, "caption": caption},
            files={"photo": image_file},
            timeout=30,
        )

    if response.status_code != 200 or not response.json().get("ok", False):
        print(f"ERROR: Telegram API request failed: {response.status_code} {response.text}", file=sys.stderr)
        sys.exit(1)

    print("Digest sent to Telegram successfully.")


if __name__ == "__main__":
    main()
