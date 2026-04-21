from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMemberUpdated
from telegram.ext import (
    ApplicationBuilder, ContextTypes, ChatJoinRequestHandler,
    CommandHandler, ChatMemberHandler
)
import json
import os
import requests
from io import BytesIO
from datetime import datetime
import asyncio

# --- Secrets/Env Variables ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
APK_URL = os.environ.get("APK_URL")
VIP_CHANNEL_URL = os.environ.get("VIP_CHANNEL_URL")
BOT_USERNAME = os.environ.get("BOT_USERNAME")
LEAVE_MSG_URL = os.environ.get("LEAVE_MSG_URL")
WELCOME_VIDEO_URL = os.environ.get("WELCOME_VIDEO_URL") 

USERS_FILE = "users.json"
LEAVE_IMAGE_URL = "https://kommodo.ai/i/UTlTK3RUQvuCGsM1aCLS"

APK_CACHE = None

# ================= USERS DATA MANAGEMENT =================
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

# ================= APK DOWNLOADER =================
def fetch_apk():
    global APK_CACHE
    try:
        if APK_URL:
            res = requests.get(APK_URL, timeout=120)
            res.raise_for_status()
            APK_CACHE = res.content
            print("APK cached ✅")
    except Exception as e:
        print("APK error:", e)

# ================= SEND APK FUNCTION =================
async def send_apk(user_id, context):
    if not APK_CACHE:
        return

    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("GET SECRET APK ✅", url=f"https://t.me/{BOT_USERNAME}?start=apk")]
    ])

    file = BytesIO(APK_CACHE)
    # File name wahi rahega jo URL se milega
    original_filename = APK_URL.split("/")[-1] if APK_URL else "premium.apk"
    file.name = original_filename

    # Updated APK Caption
    apk_caption = (
        "💰Click And Install 💰\n\n"
        "💯 Activate Panel Now 💯"
    )

    await context.bot.send_document(
        chat_id=user_id,
        document=file,
        filename=original_filename,
        caption=apk_caption,
        reply_markup=btn
    )

# ================= JOIN REQUEST HANDLER =================
async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user

    try:
        users = load_users()
        add_user(user, users)

        # Welcome Video
        welcome_text = (
            "💰How To Activate Vip Hack💰\n"
            "Pls Video Ko Pura Dekhna\n"
            "      💯 Setup Video 💯"
        )

        await context.bot.send_video(
            chat_id=user.id,
            video=WELCOME_VIDEO_URL,
            caption=welcome_text
        )

        # Send APK
        await send_apk(user.id, context)
        
        await asyncio.sleep(1.5)

        # Third Message
        promo_msg = (
            "VIP NUMBER SURESHOT CHANNEL JOIN FREEE 👇🏻👇🏻\n\n"
            "https://t.me/+7SIcw7FkDo5hMjI1\n"
            "https://t.me/+7SIcw7FkDo5hMjI1"
        )
        await context.bot.send_message(chat_id=user.id, text=promo_msg)

    except Exception as e:
        print("Join error:", e)

# ================= TRACK USER LEAVING =================
async def track_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = update.chat_member
        if member.old_chat_member.status in ["member", "administrator"] and member.new_chat_member.status in ["left", "kicked"]:
            user = member.from_user

            btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("JOIN CHANNEL 🔥", url=LEAVE_MSG_URL)]
            ])

            await context.bot.send_photo(
                chat_id=user.id,
                photo=LEAVE_IMAGE_URL,
                caption="🙌 CONGRATULATIONS 🎉 APKO AB YE SARE FREE MELNE WALA HAI ES CHANNEL ME 👇🏻",
                reply_markup=btn
            )
    except Exception as e:
        print("Leave error:", e)

# ================= BROADCAST =================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to message to broadcast")
        return

    users = load_users()
    msg = update.message.reply_to_message

    sent = 0
    for u in users:
        try:
            await msg.copy(chat_id=u["id"])
            sent += 1
            await asyncio.sleep(0.05)
        except:
            continue

    await update.message.reply_text(f"Broadcast sent to {sent} users ✅")

# ================= START COMMAND =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users = load_users()
    add_user(user, users)

    if context.args and context.args[0] == "apk":
        await send_apk(user.id, context)
    else:
        await update.message.reply_text("Click button to get APK 🔥")

# ================= MAIN EXECUTION =================
def main():
    fetch_apk()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(ChatJoinRequestHandler(join_request))
    app.add_handler(ChatMemberHandler(track_leave, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))

    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
