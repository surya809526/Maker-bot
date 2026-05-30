from flask import Flask, request
import os
import requests

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route("/", methods=["GET"])
def home():
    return "Bot Running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        if text == "/start":
            send_message(chat_id, "Hello! Main chal raha hoon ✅")
        else:
            send_message(chat_id, f"Tumne likha: {text}")
    return "OK"

@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    response = requests.post(url, json={"url": f"{WEBHOOK_URL}/webhook"})
    return response.json()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
