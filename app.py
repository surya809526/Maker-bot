from flask import Flask
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

@app.route("/")
def home():
    return f"Bot Token Found: {BOT_TOKEN is not None}, Length: {len(BOT_TOKEN) if BOT_TOKEN else 0}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
