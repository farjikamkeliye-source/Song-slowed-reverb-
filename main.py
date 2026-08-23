import os
import threading
import requests
from flask import Flask
import telebot

app = Flask(__name__)

@app.route('/')
def home():
    return "API-based Bot is alive and free!"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

TOKEN = "8858128209:AAFqS5RLVmFqvjX5yOQUqOz-ix99ojOZwtQ"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🎵 **Welcome to Audio Downloader Bot!**\n\n"
        "🔗 Kisi bhi YouTube ya Instagram ka link bhejein, yeh bot turant uska audio bhej dega."
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def process_link(message):
    url = message.text.strip()
    
    if not url.startswith("http"):
        bot.reply_to(message, "❌ Kripya ek valid link bhejein.")
        return

    msg = bot.reply_to(message, "⏳ Link process ho raha hai, thoda intezaar karein...")

    try:
        # Free public API ka use karke media info nikalna
        api_url = f"https://api.cobalt.tools/api/json"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        data = {
            "url": url,
            "isAudioOnly": True,
            "audioFormat": "mp3"
        }

        response = requests.post(api_url, json=data, headers=headers)
        res_json = response.json()

        if "url" in res_json:
            download_url = res_json["url"]
            bot.send_audio(message.chat.id, download_url, caption="✨ Yeh lijiye aapka audio!")
            bot.delete_message(message.chat.id, msg.message_id)
        elif "picker" in res_json:
            # Agar multiple options hon toh pehla utha lo
            download_url = res_json["picker"][0]["url"]
            bot.send_audio(message.chat.id, download_url, caption="✨ Yeh lijiye aapka audio!")
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            raise Exception("API se audio link nahi mila.")

    except Exception as e:
        print(e)
        bot.edit_message_text("❌ Error: Is link se audio extract nahi ho paya. Doosra link try karein.", message.chat.id, msg.message_id)

if __name__ == "__main__":
    t = threading.Thread(target=run_web)
    t.start()
    
    print("API Bot is running...")
    bot.infinity_polling()
    
