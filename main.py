from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes, ChatJoinRequestHandler,
    CommandHandler
)
from telegram.error import NetworkError, TimedOut, RetryAfter
import json
import os
import asyncio
import requests
from io import BytesIO
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")
APK_URL = os.environ.get("APK_URL")
VIP_CHANNEL_URL = os.environ.get("VIP_CHANNEL_URL", "https://t.me/yourchannel")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "YourBot")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

USERS_FILE = "users.json"
WELCOME_IMAGE_URL = "https://kommodo.ai/i/lk66ZvAY1u3vzHXU9aLN"

APK_CACHE = None


def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                return json.load(f)
    except:
        pass
    return []


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def add_user(user, users):
    if not any(u["id"] == user.id for u in users):
        users.append({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "joined_at": datetime.now().isoformat()
        })
        save_users(users)


def fetch_apk():
    global APK_CACHE
    if not APK_URL:
        print("APK_URL not set")
        return

    try:
        print("Downloading APK...")
        res = requests.get(APK_URL, timeout=120)
        res.raise_for_status()
        APK_CACHE = res.content
        print("APK cached ✅")
    except Exception as e:
        print("APK error:", e)


# ✅ FIXED FUNCTION (no indentation issue)
async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user

    for _ in range(3):
        try:
            users = load_users()
            add_user(user, users)

            btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔥 VIP CHANNEL 🔥", url=VIP_CHANNEL_URL)]
            ])

            await context.bot.send_photo(
                chat_id=user.id,
                photo=WELCOME_IMAGE_URL,
                caption="🚀 WELCOME TO PREMIUM BOT 🔥",
                reply_markup=btn
            )

            if APK_CACHE:
                file = BytesIO(APK_CACHE)
                file.name = "premium.apk"

                await context.bot.send_document(
                    chat_id=user.id,
                    document=file,
                    caption="✅ APK FILE READY 💥"
                )

            break

        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except (NetworkError, TimedOut):
            await asyncio.sleep(5)
        except Exception as e:
            print("Error:", e)
            break


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    users = load_users()
    text = " ".join(context.args)

    for u in users:
        try:
            await context.bot.send_message(chat_id=u["id"], text=text)
            await asyncio.sleep(0.05)
        except:
            pass

    await update.message.reply_text("Broadcast done ✅")


def main():
    if not BOT_TOKEN:
        print("BOT_TOKEN missing ❌")
        return

    print("Bot starting...")
    fetch_apk()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(ChatJoinRequestHandler(join_request))
    app.add_handler(CommandHandler("broadcast", broadcast))

    app.run_polling()


# ✅ FIXED MAIN CHECK
if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print("Crash:", e)
            import time
            time.sleep(10)
