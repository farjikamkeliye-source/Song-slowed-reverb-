import os
import threading
from flask import Flask
import telebot
import yt_dlp
from pydub import AudioSegment

app = Flask(__name__)

@app.route('/')
def home():
    return "Slowed & Reverb Bot is alive!"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

TOKEN = "8858128209:AAFqS5RLVmFqvjX5yOQUqOz-ix99ojOZwtQ"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🎵 **Welcome to Slowed & Reverb Bot!**\n\n"
        "🔗 Kisi bhi song ya video ka link bhejein, yeh bot uska audio download karke use **Slowed & Reverb** mein convert karke bhej dega."
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

def make_slowed_reverb(input_path, output_path):
    # Audio load karein
    song = AudioSegment.from_file(input_path)
    
    # 1. Slowed effect: Frame rate ko kam karke pitch aur speed slow karna
    new_sample_rate = int(song.frame_rate * 0.82) # 0.82 speed factor
    slowed_song = song._spawn(song.raw_data, overrides={'frame_rate': new_sample_rate})
    slowed_song = slowed_song.set_frame_rate(44100)
    
    # 2. Reverb / Echo effect: Audio ko thoda delay karke overlay karna
    echo1 = slowed_song - 6  # Thoda low volume echo
    echo2 = slowed_song - 12 # Aur kam volume echo
    
    # Mix song with echo delays
    reverbed_song = slowed_song.overlay(echo1, position=100).overlay(echo2, position=250)
    
    # Export as mp3
    reverbed_song.export(output_path, format="mp3")

@bot.message_handler(func=lambda message: True)
def process_audio(message):
    url = message.text.strip()
    
    if not url.startswith("http"):
        bot.reply_to(message, "❌ Kripya ek valid link bhejein.")
        return

    msg = bot.reply_to(message, "🎧 Audio download aur Slowed & Reverb process ho raha hai... Thoda waqt lag sakta hai.")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloaded_song.%(ext)s',
        'noplaylist': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }

    raw_file = None
    output_file = "slowed_reverb_song.mp3"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            raw_file = ydl.prepare_filename(info)

        # Python se audio ko Slowed & Reverb banayein
        make_slowed_reverb(raw_file, output_file)

        if os.path.exists(output_file):
            with open(output_file, 'rb') as audio:
                bot.send_audio(message.chat.id, audio, caption="✨ Yeh lijiye aapka Slowed & Reverb song!")
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            raise Exception("Audio process nahi ho payi.")

        # Cleanup files
        if os.path.exists(raw_file):
            os.remove(raw_file)
        if os.path.exists(output_file):
            os.remove(output_file)

    except Exception as e:
        print(e)
        if raw_file and os.path.exists(raw_file):
            os.remove(raw_file)
        if os.path.exists(output_file):
            os.remove(output_file)
        bot.edit_message_text(f"❌ Error: Link support nahi kar raha ya processing mein samasya aayi.", message.chat.id, msg.message_id)

if __name__ == "__main__":
    t = threading.Thread(target=run_web)
    t.start()
    
    print("Slowed & Reverb Bot (Pure Python) is running...")
    bot.infinity_polling()
    
