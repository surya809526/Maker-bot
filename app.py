from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return str(os.environ.get("BOT_TOKEN"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
