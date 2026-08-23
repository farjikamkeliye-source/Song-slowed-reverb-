import os
import threading
from flask import Flask
import telebot
import yt_dlp

app = Flask(__name__)

@app.route('/')
def home():
    return "Slowed & Reverb Bot is alive and free!"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

TOKEN = "8858128209:AAFqS5RLVmFqvjX5yOQUqOz-ix99ojOZwtQ"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🎵 **Welcome to Slowed & Reverb Bot!**\n\n"
        "🔗 Kisi bhi song ya video ka link bhejein, yeh bot use **Slowed & Reverb** mein convert karke bhej dega."
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def process_audio(message):
    url = message.text.strip()
    
    if not url.startswith("http"):
        bot.reply_to(message, "❌ Kripya ek valid link bhejein.")
        return

    msg = bot.reply_to(message, "🎧 Audio download aur Slowed & Reverb process ho raha hai... Thoda waqt lag sakta hai.")

    current_dir = os.getcwd()
    os.environ["PATH"] += os.pathsep + current_dir

    # Anti-block options for free hosting servers like Render
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'input_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'postprocessor_args': [
            '-af', 'asetrate=44100*0.85,aresample=44100,aecho=0.8:0.88:60:0.4'
        ],
        'noplaylist': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    output_file = "input_audio.mp3"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists(output_file):
            with open(output_file, 'rb') as audio:
                bot.send_audio(message.chat.id, audio, caption="✨ Yeh lijiye aapka Slowed & Reverb song!")
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            raise Exception("Audio process nahi ho payi.")

        if os.path.exists(output_file):
            os.remove(output_file)

    except Exception as e:
        print(e)
        if os.path.exists(output_file):
            os.remove(output_file)
        bot.edit_message_text(f"❌ Error: Link download nahi ho paya. Kripya doosra link try karein.", message.chat.id, msg.message_id)

if __name__ == "__main__":
    t = threading.Thread(target=run_web)
    t.start()
    
    print("Bot is running...")
    bot.infinity_polling()
    
