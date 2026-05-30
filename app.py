from flask import Flask, request
import os
import requests
import urllib.parse
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

user_styles = {}
user_history = {}

STYLES = {
    "tech": "dark blue black background, glowing neon blue circuit boards, terminal screen with code, dramatic lighting, 4K, photorealistic, no text no words no letters",
    "horror": "dark horror background, scary atmosphere, blood red elements, dramatic shadows, 4K, photorealistic, no text no words no letters",
    "gaming": "gaming setup background, colorful RGB lights, dark room, gaming chair, 4K, photorealistic, no text no words no letters",
    "youtube": "dramatic YouTube thumbnail background, dark moody lighting, glowing elements, professional studio, 4K, no text no words no letters",
    "gemini": "dark blue background, Google Gemini glowing diamond shape, terminal code screen green text, Telegram blue logo, tech elements, 4K, no text no words no letters",
    "default": "professional YouTube thumbnail background, dramatic lighting, vibrant colors, 4K ultra HD, no text no words no letters"
}

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})

def send_photo(chat_id, image_bytes, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    requests.post(url, data={"chat_id": chat_id, "caption": caption}, files={"photo": ("thumbnail.png", image_bytes, "image/png")})

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = current + " " + word if current else word
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] > max_width and current:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)
    return lines

def add_text_overlay(image_bytes, title):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    img = img.resize((1280, 720))

    # Dark gradient overlay neeche
    overlay = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    for i in range(300):
        alpha = int(200 * (i / 300))
        draw_overlay.rectangle([(0, 420 + i), (1280, 421 + i)], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img, overlay)

    draw = ImageDraw.Draw(img)

    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 85)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 65)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
    except:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large

    title_upper = title.upper()

    # Font size decide karo text length ke hisab se
    if len(title_upper) < 20:
        font = font_large
    elif len(title_upper) < 35:
        font = font_medium
    else:
        font = font_small

    lines = wrap_text(draw, title_upper, font, 1220)
    lines = lines[:3]

    total_height = len(lines) * 90
    y = 720 - total_height - 30

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (1280 - text_width) // 2

        # Black shadow
        for dx, dy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4), (4, 0)]:
            draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 255))

        # Yellow text
        draw.text((x, y), line, font=font, fill=(255, 215, 0, 255))
        y += 90

    final = img.convert("RGB")
    output = io.BytesIO()
    final.save(output, format="PNG")
    return output.getvalue()

def generate_thumbnail(prompt, style="default"):
    style_prompt = STYLES.get(style, STYLES["default"])
    full_prompt = f"{prompt}, {style_prompt}"
    encoded = urllib.parse.quote(full_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1280&height=720&nologo=true"
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            return response.content
        return None
    except Exception as e:
        print(f"Error: {e}")
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
/style youtube - Viral YouTube style
/style gemini - Gemini AI style
/history - Purane thumbnails dekho

Example:
/style tech
/thumbnail I Built My Own AI Bot"""
        send_message(chat_id, msg)

    elif text.startswith("/style"):
        parts = text.split()
        if len(parts) < 2:
            send_message(chat_id, "Style likho!\n\nAvailable styles:\n• tech\n• horror\n• gaming\n• youtube\n• gemini")
        else:
            style = parts[1].lower()
            if style in STYLES:
                user_styles[chat_id] = style
                send_message(chat_id, f"✅ Style set: <b>{style}</b>")
            else:
                send_message(chat_id, "❌ Valid styles: tech, horror, gaming, youtube, gemini")

    elif text.startswith("/thumbnail"):
        parts = text.split(" ", 1)
        if len(parts) < 2:
            send_message(chat_id, "Title likho!\nExample: /thumbnail I Built My Own AI Bot")
        else:
            title = parts[1]
            style = user_styles.get(chat_id, "default")
            send_message(chat_id, f"⏳ Thumbnail ban raha hai... ({style} style)\n\nThoda wait karo ~30 sec ⏱")
            image = generate_thumbnail(title, style)
            if image:
                final_image = add_text_overlay(image, title)
                if chat_id not in user_history:
                    user_history[chat_id] = []
                user_history[chat_id].append({
                    "title": title,
                    "style": style,
                    "time": datetime.now().strftime("%d/%m %H:%M")
                })
                send_photo(chat_id, final_image, f"🎨 {title} ({style} style)")
            else:
                send_message(chat_id, "❌ Error aaya, dobara try karo!")

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
