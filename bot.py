"""Minimal Telegram bot that opens the Gift Crafting Optimizer Mini App.

Requires:
  - A bot token from @BotFather (set BOT_TOKEN env var or edit below).
  - A publicly hosted HTTPS URL for miniapp.html (set MINIAPP_URL).

Run:  python bot.py
No external dependencies (stdlib only).
"""
import json
import os
import time
import urllib.request

BOT_TOKEN = os.environ.get("BOT_TOKEN", "PASTE_YOUR_BOT_TOKEN_HERE")
MINIAPP_URL = os.environ.get("MINIAPP_URL", "https://dockfixlabs.github.io/gift-crafting-optimizer/miniapp.html")
API = "https://api.telegram.org/bot" + BOT_TOKEN

HELP_TEXT = (
    "Gift Crafting Optimizer\n\n"
    "Computes Telegram Star Gift crafting probabilities from documented rules.\n"
    "No login required. No trading. Probabilities are estimates.\n\n"
    "Commands:\n"
    "/start - Open the calculator\n"
    "/about - About this bot\n"
    "/help - This message"
)

ABOUT_TEXT = (
    "Gift Crafting Optimizer v1.0\n"
    "Evidence-based. No hype. No patent claims.\n"
    "Source: core.telegram.org/api/gifts\n"
    "Market data: static sample (Fragment, Oct 2026)."
)


def api(method, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API + "/" + method, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return api("sendMessage", payload)


def main():
    if "PASTE_YOUR" in BOT_TOKEN:
        print("ERROR: set BOT_TOKEN env var or edit bot.py")
        return
    offset = 0
    print("Bot running. Send /start to your bot in Telegram.")
    while True:
        try:
            res = api("getUpdates", {"offset": offset, "timeout": 25})
            for upd in res.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message") or {}
                chat_id = (msg.get("chat") or {}).get("id")
                text = (msg.get("text") or "").strip()
                if not chat_id:
                    continue
                if text.startswith("/start"):
                    send(chat_id, "Gift Crafting Optimizer — compute crafting probabilities from documented Telegram rules.", {
                        "inline_keyboard": [[{"text": "Open Calculator", "web_app": {"url": MINIAPP_URL}}]]
                    })
                elif text.startswith("/help"):
                    send(chat_id, HELP_TEXT)
                elif text.startswith("/about"):
                    send(chat_id, ABOUT_TEXT)
                else:
                    send(chat_id, "Unknown command. Use /help.")
        except Exception as e:
            print("loop error:", e)
            time.sleep(3)


if __name__ == "__main__":
    main()