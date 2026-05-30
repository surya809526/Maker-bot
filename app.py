import os
import requests
from flask import Flask, request

TOKEN = os.environ.get("TOKEN", "")
HF_API_KEY = os.environ.get("HF_API_KEY", "")

# 🚀 UPDATE: Aapka naya Render Webhook URL yahan set kar diya hai
WEBHOOK_URL = "https://maker-bot-x9ob.onrender.com"

app = Flask(__name__)

def translate_hindi_to_english(text):
    try:
        api_url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={requests.utils.quote(text)}"
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            result = response.json()
            return "".join([sentence[0] for sentence in result[0]])
    except Exception as e:
        print(f"Translation Error: {e}")
    return text

@app.route("/", methods=["GET", "POST", "HEAD"])
def index():
    if request.method == "HEAD":
        return "OK", 200

    if request.method == "GET":
        if not TOKEN:
            return "<h1>Error: TOKEN variable missing on Render!</h1>", 500
        telegram_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
        params = {"url": f"{WEBHOOK_URL}/"}
        res = requests.get(telegram_url, params=params).json()
        if res.get("ok"):
            return f"<h1>Booster Thumbnail Bot Live on New Server!</h1>", 200
        return f"<h1>Failed: {res.get('description')}</h1>", 500

    if request.method == "POST":
        try:
            data = request.get_json()
            if data and "message" in data:
                message = data["message"]
                chat_id = message["chat"]["id"]
                text = message.get("text", "")

                if not TOKEN:
                    return "OK", 200

                if text == "/start":
                    send_message(chat_id, "🚀 Booster AI Thumbnail Bot Active!\n\nApna shocking ya horror idea Hindi me bhejein, bot bade creators jaisa automatic boost lagakar render karega!")
                elif text:
                    english_prompt = translate_hindi_to_english(text)
                    send_message(chat_id, f"🎨 Idea: '{text}'\n🤖 High-expression engine par render ho raha hai...")
                    generate_boosted_thumbnail(chat_id, english_prompt)
        except Exception as e:
            print(f"Webhook Error: {e}")
        return "OK", 200

def send_message(chat_id, text):
    if not TOKEN: return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def generate_boosted_thumbnail(chat_id, english_prompt):
    try:
        if not TOKEN or not HF_API_KEY:
            send_message(chat_id, "❌ Error: API Key ya Token missing hai!")
            return
        
        API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
        headers = {"Authorization": f"Bearer {HF_API_KEY.strip()}"}
        
        # KEYWORDS BOOSTER: Close-up aur expressions ko auto-boost karne ke liye
        boosted_prompt = (
            f"Extreme close-up portrait of {english_prompt}, "
            f"highly detailed face with extreme shocked expression, eyes wide open, mouth agape, "
            f"intense emotion, realistic skin texture, sharp focus, dynamic colorful rim lighting, "
            f"gaming youtube thumbnail style, professional cinematography, 8k, ultra-detailed, no text, 16:9 aspect ratio"
        )
        
        payload = {"inputs": boosted_prompt}
        response = requests.post(API_URL, headers=headers, json=payload, timeout=35)

        if response.status_code == 200:
            output_path = f"/tmp/boost_thumb_{chat_id}.jpg"
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            with open(output_path, 'rb') as photo:
                files = {'photo': photo}
                data = {'chat_id': chat_id, 'caption': f"✅ Shocking Thumbnail Ready!"}
                requests.post(url, data=data, files=files)
                
            if os.path.exists(output_path):
                os.remove(output_path)
        else:
            # Automatic Fallback backup engine
            fallback_url = f"https://image.pollinations.ai/p/{requests.utils.quote(boosted_prompt)}?width=1280&height=720&model=flux"
            res = requests.get(fallback_url, timeout=30)
            if res.status_code == 200:
                output_path = f"/tmp/boost_fb_{chat_id}.jpg"
                with open(output_path, 'wb') as f: f.write(res.content)
                url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
                with open(output_path, 'rb') as photo:
                    requests.post(url, data={'chat_id': chat_id, 'caption': '✅ Thumbnail Ready!'}, files={'photo': photo})
                if os.path.exists(output_path): os.remove(output_path)
            else:
                send_message(chat_id, f"❌ Engine Busy: status {response.status_code}")
            
    except Exception as e:
        send_message(chat_id, f"❌ Error: {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
