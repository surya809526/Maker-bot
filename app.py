import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN missing")

app = Flask(__name__)

# Telegram app
tg_app = Application.builder().token(BOT_TOKEN).build()


# ---------------- HANDLERS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Thumbnail Bot Ready!\nSend text for thumbnail idea.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Thumbnail prompt generator
    prompt = f"""
🎨 Thumbnail Idea:
- Text: {text}
- Style: cinematic, high contrast, viral YouTube thumbnail
- Elements: dramatic background, bold text, glowing effect
"""

    await update.message.reply_text(prompt)


tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


# ---------------- FLASK ----------------
@app.route("/")
def home():
    return "Bot Running OK"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    update = Update.de_json(data, tg_app.bot)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(tg_app.process_update(update))

    return "ok"


@app.route("/setwebhook")
def set_webhook():
    url = f"{APP_URL}/webhook"
    tg_app.bot.set_webhook(url=url)
    return f"Webhook set: {url}"


# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
