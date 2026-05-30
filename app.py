from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return f"""
    TEST_VAR={os.getenv('TEST_VAR')}
    <br>
    BOT_TOKEN_EXISTS={os.getenv('BOT_TOKEN') is not None}
    <br>
    HF_API_KEY_EXISTS={os.getenv('HF_API_KEY') is not None}
    """

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
