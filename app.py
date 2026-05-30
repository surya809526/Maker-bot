import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ---------------- LOGGING ----------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ---------------- CONFIG ----------------
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Render/Env me set karna
APP_URL = os.getenv("APP_URL")      # https://your-app.onrender.com

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN missing in environment variables")

# ---------------- FLASK APP ----------------
app = Flask(__name__)

# ---------------- TELEGRAM APP ----------------
tg_app = Application.builder().token(BOT_TOKEN).build()

# ---------------- HANDLERS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bot started successfully!")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send any message and I will reply back.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"📩 You said: {text}")

# Add handlers
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("help", help_cmd))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


# ---------------- FLASK ROUTES ----------------
@app.route("/")
def home():
    return "🤖 Bot is running!"

@app.route("/webhook", methods=["POST"])
async def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, tg_app.bot)
        await tg_app.process_update(update)
        return "ok"
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return "error", 500


# ---------------- SET WEBHOOK ----------------
@app.route("/setwebhook")
def set_webhook():
    url = f"{APP_URL}/webhook"
    result = tg_app.bot.set_webhook(url=url)
    return f"Webhook set to {url} => {result}"


# ---------------- MAIN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
