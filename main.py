from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes, ChatJoinRequestHandler,
    CommandHandler
)
import json
import os
import requests
from io import BytesIO
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")
APK_URL = os.environ.get("APK_URL")
VIP_CHANNEL_URL = os.environ.get("VIP_CHANNEL_URL")
BOT_USERNAME = os.environ.get("BOT_USERNAME")

USERS_FILE = "users.json"
WELCOME_IMAGE_URL = "https://kommodo.ai/i/lk66ZvAY1u3vzHXU9aLN"

APK_CACHE = None


# ================= USERS =================
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


# ================= APK CACHE =================
def fetch_apk():
    global APK_CACHE
    if not APK_URL:
        print("APK_URL not set ❌")
        return
    try:
        res = requests.get(APK_URL, timeout=120)
        res.raise_for_status()
        APK_CACHE = res.content
        print("APK cached ✅")
    except Exception as e:
        print("APK error:", e)


# ================= SEND APK =================
async def send_apk(user_id, context):
    if not APK_CACHE:
        print("APK not available ❌")
        return

    apk_btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("GET SECRET APK ✅", url=f"https://t.me/{BOT_USERNAME}?start=apk")]
    ])

    file = BytesIO(APK_CACHE)
    file.name = "jai club premium.apk"

    await context.bot.send_document(
        chat_id=user_id,
        document=file,
        filename="jai club premium.apk",
        caption=(
            "✅ 100% BEST APK IN WHOLE TELEGRAM 💥\n\n"
            "( ONLY FOR PREMIUM USERS ⚡️ )\n\n"
            "HOW TO USE - https://t.me/JaiclubNumberHack/5\n\n"
            "FOR HELP @Rd_hereee"
        ),
        reply_markup=apk_btn
    )


# ================= JOIN REQUEST =================
async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user

    try:
        users = load_users()
        add_user(user, users)

        # 🔥 VIP button
        vip_btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔥 VIP CHANNEL LINK 🔥", url=VIP_CHANNEL_URL)]
        ])

        # 🚀 Welcome image + msg
        await context.bot.send_photo(
            chat_id=user.id,
            photo=WELCOME_IMAGE_URL,
            caption="🚀🔥 WELCOME TO RD TRADERS PREMIUM BOT 🔥",
            reply_markup=vip_btn
        )

        # 📦 APK send
        await send_apk(user.id, context)

        print(f"Join request received: {user.id}")

    except Exception as e:
        print(f"Join error: {e}")


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    users = load_users()
    add_user(user, users)

    if context.args and context.args[0] == "apk":
        await send_apk(user.id, context)
    else:
        await update.message.reply_text("Click button to get APK 🔥")


# ================= MAIN =================
def main():
    print("Bot starting...")
    fetch_apk()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(ChatJoinRequestHandler(join_request))
    app.add_handler(CommandHandler("start", start))

    app.run_polling(drop_pending_updates=True)


# ================= AUTO RESTART =================
if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"Crash: {e}")
            import time
            time.sleep(10)
