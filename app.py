from flask import Flask, request
import os
import requests

app = Flask(name)

BOT_TOKEN = os.getenv("BOT_TOKEN")

@app.route("/", methods=["GET", "POST"])
def webhook():

if request.method == "GET":
    return "Bot Running"

data = request.get_json()

try:
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": "✅ Bot Working!"
            }
        )

except Exception as e:
    print(e)

return "OK"

if name == "main":
app.run(
host="0.0.0.0",
port=int(os.environ.get("PORT", 10000))
)
