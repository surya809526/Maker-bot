from flask import Flask, request
import requests
import os

app = Flask(name)

BOT_TOKEN = os.getenv("BOT_TOKEN")

def send_message(chat_id, text):
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
requests.post(url, json={
"chat_id": chat_id,
"text": text
})

@app.route("/", methods=["GET", "POST"])
def webhook():

if request.method == "GET":
    return "Bot Running"

data = request.get_json()

if data and "message" in data:
    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    if text == "/start":
        send_message(
            chat_id,
            "🚀 Thumbnail Bot Active!\n\nApna prompt bhejo."
        )
    else:
        send_message(
            chat_id,
            f"Prompt Received:\n{text}"
        )

return "OK"

if name == "main":
app.run(
host="0.0.0.0",
port=int(os.environ.get("PORT", 10000))
)
