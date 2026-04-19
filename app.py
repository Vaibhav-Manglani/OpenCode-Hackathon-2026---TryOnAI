from telegram.request import HTTPXRequest
import asyncio
from main import generate_image
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_KEY")

user_state = {}
user_images = {}

# ---------- UI ----------


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📸 Put it on a model", callback_data="tryon")],
        [InlineKeyboardButton("✏️ Redesign jewellery",
                              callback_data="redesign")],
        [InlineKeyboardButton("📱 Social media post", callback_data="social")]
    ])


def sub_menu(mode):
    if mode == "tryon":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🇮🇳 Indian Traditional",
                                  callback_data="tryon_indian")],
            [InlineKeyboardButton("🌍 Western Modern",
                                  callback_data="tryon_western")],
            [InlineKeyboardButton("👰 Bridal", callback_data="tryon_bridal")]
        ])

    elif mode == "redesign":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("A — Refined", callback_data="redesign_A")],
            [InlineKeyboardButton("B — Minimal", callback_data="redesign_B")],
            [InlineKeyboardButton("C — Material Swap",
                                  callback_data="redesign_C")],
            [InlineKeyboardButton("D — Fusion", callback_data="redesign_D")]
        ])

    elif mode == "social":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📸 Instagram Post",
                                  callback_data="social_post")],
            [InlineKeyboardButton("📱 Story", callback_data="social_story")],
            [InlineKeyboardButton("📰 Facebook", callback_data="social_fb")]
        ])


def generate_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Generate", callback_data="generate")],
        [InlineKeyboardButton("🏠 Main menu", callback_data="menu")]
    ])


def retry_menu(mode):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Try again", callback_data=mode)],
        [InlineKeyboardButton("🏠 Main menu", callback_data="menu")]
    ])

# ---------- START ----------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_state[user_id] = {"mode": None, "submode": None}

    await update.message.reply_text(
        "Hey 👋 I'm TryOnAI.\nWhat would you like to do?",
        reply_markup=main_menu()
    )

# ---------- BUTTON ----------


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    choice = query.data

    # RESET
    if choice == "menu":
        user_state[user_id] = {"mode": None, "submode": None}
        user_images[user_id] = []

        await query.message.reply_text(
            "What would you like to do?",
            reply_markup=main_menu()
        )
        return

    # STEP 1: MAIN MODE
    if choice in ["tryon", "redesign", "social"]:
        user_state[user_id] = {"mode": choice, "submode": None}
        user_images[user_id] = []

        await query.message.reply_text(
            "Choose a style:",
            reply_markup=sub_menu(choice)
        )
        return

    # STEP 2: SUBMODE
    if "_" in choice:
        mode, sub = choice.split("_", 1)

        user_state[user_id] = {"mode": mode, "submode": sub}
        user_images[user_id] = []

        await query.message.reply_text(
            "Send image(s), then click Generate.",
            reply_markup=generate_menu()
        )
        return

    # GENERATE
    if choice == "generate":
        state = user_state.get(user_id)

        if not state or not user_images.get(user_id):
            await query.message.reply_text("Upload images first.")
            return

        await query.message.reply_text("Generating... ⏳")

        try:
            outputs = generate_image(
                state["mode"],
                user_images[user_id],
                submode=state["submode"]
            )

            for img in outputs:
                with open(img, "rb") as f:
                    await query.message.reply_photo(photo=f)

            await query.message.reply_text(
                "What next?",
                reply_markup=retry_menu(state["mode"])
            )

        except Exception as e:
            await query.message.reply_text(f"Error: {e}")

# ---------- PHOTO ----------


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    state = user_state.get(user_id)
    if not state or not state["mode"]:
        await update.message.reply_text(
            "Pick an option first.",
            reply_markup=main_menu()
        )
        return

    mode = state["mode"]

    os.makedirs("uploads", exist_ok=True)

    if user_id not in user_images:
        user_images[user_id] = []

    # restrict for redesign/social
    if mode in ["redesign", "social"] and len(user_images[user_id]) >= 1:
        await update.message.reply_text("Only 1 image allowed.")
        return

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)

    idx = len(user_images[user_id]) + 1
    path = f"uploads/{user_id}_{idx}.jpg"

    await file.download_to_drive(path)
    user_images[user_id].append(path)

    await update.message.reply_text(f"Image {idx} received 👍")

    # debounce for tryon only
    if mode == "tryon":
        if "debounce" in context.user_data:
            context.user_data["debounce"].cancel()

        async def send_menu():
            await asyncio.sleep(5)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Ready when you are.",
                reply_markup=generate_menu()
            )

        task = asyncio.create_task(send_menu())
        context.user_data["debounce"] = task

    else:
        await update.message.reply_text(
            "Ready when you are.",
            reply_markup=generate_menu()
        )

# ---------- TEXT ----------


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send an image.",
        reply_markup=main_menu()
    )

# ---------- MAIN ----------


def main():
    request = HTTPXRequest(read_timeout=60.0)

    app = ApplicationBuilder().token(BOT_TOKEN).request(request).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
