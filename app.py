from flask import Flask
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")

@app.route("/")
def home():

    return f"""
    <h2>Render Environment Test</h2>

    BOT_TOKEN Found:
    {BOT_TOKEN is not None}

    <br><br>

    HF_API_KEY Found:
    {HF_API_KEY is not None}

    <br><br>

    BOT_TOKEN Length:
    {len(BOT_TOKEN) if BOT_TOKEN else 0}

    <br><br>

    HF_API_KEY Length:
    {len(HF_API_KEY) if HF_API_KEY else 0}
    """

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
