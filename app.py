from flask import Flask, request
import os
import requests
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_TOKEN = os.getenv("HF_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"

user_styles = {}
user_history = {}

STYLES = {
    "tech": "futuristic technology style, blue neon lights, circuit boards, 4K, ultra HD, YouTube thumbnail",
    "horror": "dark horror style, scary, blood red, dark atmosphere, 4K, ultra HD, YouTube thumbnail",
    "gaming": "gaming style, colorful, action packed, RGB lights, 4K, ultra HD, YouTube thumbnail",
    "default": "professional YouTube thumbnail, vibrant colors, 4K, ultra HD, eye catching"
}

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})

def send_photo(chat_id, image_bytes, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    requests.post(url, data={"chat_id": chat_id, "caption": caption}, files={"photo": ("thumbnail.png", image_bytes, "image/png")})

def generate_thumbnail(prompt, style="default"):
    style_prompt = STYLES.get(style, STYLES["default"])
    full_prompt = f"{prompt}, {style_prompt}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": full_prompt}
    response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)
    if response.status_code == 200:
        return response.content
    return None

@app.route("/", methods=["GET"])
def home():
    return "Bot Running"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" not in data:
        return "OK"

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    if text == "/start":
        msg = """🎨 <b>YouTube Thumbnail Generator Bot</b>

Commands:
/thumbnail [title] - Thumbnail banao
/style tech - Tech style
/style horror - Horror style
/style gaming - Gaming style
/history - Purane thumbnails dekho

Example: /thumbnail AI ka future"""
        send_message(chat_id, msg)

    elif text.startswith("/style"):
        parts = text.split()
        if len(parts) < 2:
            send_message(chat_id, "Style likho! Example: /style tech")
        else:
            style = parts[1].lower()
            if style in STYLES:
                user_styles[chat_id] = style
                send_message(chat_id, f"✅ Style set: <b>{style}</b>")
            else:
                send_message(chat_id, "❌ Valid styles: tech, horror, gaming")

    elif text.startswith("/thumbnail"):
        parts = text.split(" ", 1)
        if len(parts) < 2:
            send_message(chat_id, "Title likho! Example: /thumbnail AI ka future")
        else:
            title = parts[1]
            style = user_styles.get(chat_id, "default")
            send_message(chat_id, f"⏳ Thumbnail ban raha hai... ({style} style)")
            image = generate_thumbnail(title, style)
            if image:
                if chat_id not in user_history:
                    user_history[chat_id] = []
                user_history[chat_id].append({
                    "title": title,
                    "style": style,
                    "time": datetime.now().strftime("%d/%m %H:%M")
                })
                send_photo(chat_id, image, f"🎨 {title} ({style} style)")
            else:
                send_message(chat_id, "❌ Model load ho raha hai, 1 minute baad try karo!")

    elif text == "/history":
        history = user_history.get(chat_id, [])
        if not history:
            send_message(chat_id, "📭 Koi history nahi hai abhi")
        else:
            msg = "📋 <b>Tumhari History:</b>\n\n"
            for i, item in enumerate(history[-5:], 1):
                msg += f"{i}. {item['title']} ({item['style']}) - {item['time']}\n"
            send_message(chat_id, msg)

    else:
        send_message(chat_id, "Commands ke liye /start likho")

    return "OK"

@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    response = requests.post(url, json={"url": f"{WEBHOOK_URL}/webhook"})
    return response.json()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
