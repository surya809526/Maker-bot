import os
import requests
from flask import Flask, request

# Telegram Bot Token
TOKEN = os.getenv("BOT_TOKEN", "")

# Hugging Face API Key
HF_API_KEY = os.getenv("HF_API_KEY", "")

# Render URL
WEBHOOK_URL = "https://maker-bot-x9ob.onrender.com"

app = Flask(__name__)

def translate_hindi_to_english(text):
    try:
        api_url = (
            "https://translate.googleapis.com/translate_a/single"
            f"?client=gtx&sl=auto&tl=en&dt=t&q={requests.utils.quote(text)}"
        )

        response = requests.get(api_url, timeout=10)

        if response.status_code == 200:
            result = response.json()
            return "".join([x[0] for x in result[0]])

    except Exception as e:
        print("Translation Error:", e)

    return text

@app.route("/", methods=["GET", "POST", "HEAD"])
def index():

    if request.method == "HEAD":
        return "OK", 200

    if request.method == "GET":

        if not TOKEN:
            return "<h1>BOT_TOKEN missing on Render</h1>", 500

        telegram_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"

        response = requests.get(
            telegram_url,
            params={"url": WEBHOOK_URL}
        )

        return f"Bot Running<br>{response.text}", 200

    return "OK", 200
