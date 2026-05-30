from flask import Flask, request
import os
import requests

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

@app.route("/", methods=["GET", "POST"])
def webhook():

    if request.method == "GET":
        return "Bot Running"

    data = request.get_json()

    print(data)

    return "OK"

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
