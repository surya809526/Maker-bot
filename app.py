from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return f"""
BOT_TOKEN EXISTS: {"BOT_TOKEN" in os.environ}<br>
HF_API_KEY EXISTS: {"HF_API_KEY" in os.environ}
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
