from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes, ChatJoinRequestHandler,
    CommandHandler, ChatMemberHandler
)
from telegram.error import NetworkError, TimedOut, RetryAfter
import json
import os
import sys
import asyncio
import requests
from io import BytesIO
from datetime import datetime

sys.stdout.reconfigure(line_buffering=True)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
APK_URL = os.environ.get("APK_URL")
VIP_CHANNEL_URL = os.environ.get("VIP_CHANNEL_URL", "https://t.me/yourchannel")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "YourBot")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

USERS_FILE = "users.json"
WELCOME_IMAGE_URL = "https://kommodo.ai/i/lk66ZvAY1u3vzHXU9aLN"
LEAVE_IMAGE_URL = "https://kommodo.ai/i/BZJOSOTFvIlJnDQDropG"
LEAVE_CAPTION = (
    "🙌 CONGRATULATIONS 🎉 APKO AB YE SARE FREE MELNE WALA HAI ES CHANNEL ME 👇🏻\n\n"
    "https://t.me/+xzK_Cl8j_YxlODhl\n"
    "https://t.me/+xzK_Cl8j_YxlODhl"
)

APK_CACHE = None


def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return []


def save_users(users):
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
    except IOError as e:
        print(f"Error saving users: {e}")


def add_user(user, users):
    if not any(u["id"] == user.id for u in users):
        users.append({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "joined_at": datetime.now().isoformat()
        })
        save_users(users)
    return users


def fetch_apk_at_startup():
    global APK_CACHE
    if not APK_URL:
        print("WARNING: APK_URL not set — APK will not be sent.")
        return
    try:
        print("Downloading APK from GitHub...")
        response = requests.get(APK_URL, timeout=120)
        response.raise_for_status()
        APK_CACHE = response.content
        print(f"APK cached successfully ({len(APK_CACHE)} bytes)")
    except Exception as e:
        print(f"Failed to download APK: {e}")
        APK_CACHE = None


async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user

    for attempt in range(3):
        try:
            users = load_users()
            add_user(user, users)

            welcome_button = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔥 VIP CHANNEL LINK 🔥", url=VIP_CHANNEL_URL)]
            ])

            await context.bot.send_photo(
                chat_id=user.id,
                photo=WELCOME_IMAGE_URL,
                caption="🚀🔥 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 JAI CLUB 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗕𝗢𝗧 🔥",
                reply_markup=welcome_button
            )

            if APK_CACHE:
                apk_button = InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        "💀 𝙎𝙀𝘾𝙍𝙀𝙏 𝘼𝙋𝙆 𝙁𝙄𝙇𝙀🔥",
                        url=f"https://t.me/{BOT_USERNAME}?start=apk"
                    )]
                ])
                apk_file = BytesIO(APK_CACHE)
                apk_file.name = "𝐉𝐀𝐈𝐂𝐋𝐔𝐁_𝐍𝐔𝐌𝐁𝐄𝐑_𝐇𝐀𝐂𝐊_1_00.apk"
                await context.bot.send_document(
                    chat_id=user.id,
                    document=apk_file,
                    filename="𝐉𝐀𝐈𝐂𝐋𝐔𝐁_𝐍𝐔𝐌𝐁𝐄𝐑_𝐇𝐀𝐂𝐊_1_00.apk",
                    caption=(
                        "✅ 100% NUMBER HACK 💥\n\n"
                        "( ONLY FOR PREMIUM USERS ⚡️ )\n"
                        "( 100% LOSS RECOVER GUARANTEE ⚡️ )\n\n"
                        "𝐇𝐎𝐖 𝐓𝐎 𝐔𝐒𝐄 𝐇𝐀𝐂𝐊 :- https://t.me/JaiclubNumberHack/5\n"
                        "FOR HELP  @Rd_hereee"
                    ),
                    reply_markup=apk_button
                )
                print(f"APK sent to: {user.id} (@{user.username})")
            else:
                print(f"APK cache empty, not sent to: {user.id}")

            break

        except RetryAfter as e:
            print(f"Rate limited, waiting {e.retry_after}s...")
            await asyncio.sleep(e.retry_after)
        except (NetworkError, TimedOut) as e:
            print(f"Network error attempt {attempt + 1}/3: {e}")
            if attempt < 2:
                await asyncio.sleep(5)
        except Exception as e:
            print(f"Error for {user.id}: {e}")
            break


async def member_left(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.chat_member:
        return
    old_status = update.chat_member.old_chat_member.status
    new_status = update.chat_member.new_chat_member.status
    if old_status in ["member", "administrator", "creator"] and new_status in ["left", "kicked"]:
        user = update.chat_member.new_chat_member.user
        try:
            await context.bot.send_photo(
                chat_id=user.id,
                photo=LEAVE_IMAGE_URL,
                caption=LEAVE_CAPTION
            )
            print(f"Leave msg sent to: {user.id} (@{user.username})")
        except Exception as e:
            print(f"Could not send leave msg to {user.id}: {e}")


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    users = load_users()
    if not users:
        await update.message.reply_text("No users yet.")
        return

    msg = update.message
    caption_text = " ".join(context.args) if context.args else None
    success = 0
    failed = 0

    broadcast_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 VIP CHANNEL LINK 🔥", url=VIP_CHANNEL_URL)]
    ])

    if not msg.reply_to_message and not caption_text:
        await update.message.reply_text(
            "Usage:\n"
            "1. Kisi message ko reply karo + /broadcast\n"
            "2. /broadcast apna message text"
        )
        return

    await update.message.reply_text(f"📤 Broadcasting to {len(users)} users...")

    for user_data in users:
        try:
            if msg.reply_to_message:
                replied = msg.reply_to_message
                if replied.photo:
                    await context.bot.send_photo(
                        chat_id=user_data["id"],
                        photo=replied.photo[-1].file_id,
                        caption=caption_text or replied.caption or "",
                        reply_markup=broadcast_button
                    )
                elif replied.video:
                    await context.bot.send_video(
                        chat_id=user_data["id"],
                        video=replied.video.file_id,
                        caption=caption_text or replied.caption or "",
                        reply_markup=broadcast_button
                    )
                elif replied.document:
                    await context.bot.send_document(
                        chat_id=user_data["id"],
                        document=replied.document.file_id,
                        caption=caption_text or replied.caption or "",
                        reply_markup=broadcast_button
                    )
                elif replied.text:
                    await context.bot.send_message(
                        chat_id=user_data["id"],
                        text=caption_text or replied.text,
                        reply_markup=broadcast_button
                    )
            else:
                await context.bot.send_message(
                    chat_id=user_data["id"],
                    text=caption_text,
                    reply_markup=broadcast_button
                )

            success += 1
            await asyncio.sleep(0.05)

        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
            failed += 1
        except Exception as e:
            print(f"Broadcast failed for {user_data['id']}: {e}")
            failed += 1

    await update.message.reply_text(
        f"✅ Broadcast done!\nSuccess: {success}\nFailed: {failed}\nTotal: {len(users)}"
    )


def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN not set")
        import time
        time.sleep(30)
        return

    print(f"[{datetime.now()}] Starting bot...")
    fetch_apk_at_startup()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(join_request))
    app.add_handler(ChatMemberHandler(member_left, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(CommandHandler("broadcast", broadcast))

    print(f"[{datetime.now()}] Bot running (polling)...")

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["chat_join_request", "chat_member", "message"]
    )


if name == "main":
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print("Bot stopped.")
            break
        except Exception as e:
            print(f"[{datetime.now()}] Crashed: {e}")
            print("Restarting in 10s...")
            import time
            time.sleep(10)
