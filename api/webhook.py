import os
import telebot
import httpx
from http.server import BaseHTTPRequestHandler

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
INCEPTION_API_KEY = os.environ["INCEPTION_API_KEY"]

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)


def ask_ai(user_text):
    headers = {
        "Authorization": f"Bearer {INCEPTION_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mercury-2",
        "reasoning_effort": "low",
        "messages": [{"role": "user", "content": user_text}]
    }
    with httpx.Client(timeout=25) as client:
        response = client.post(
            "https://api.inceptionlabs.ai/v1/chat/completions",
            json=payload,
            headers=headers
        )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


@bot.message_handler(content_types=['text'])
def handle_text(message):
    print(f"HANDLER TRIGGERED (text): {message.text}", flush=True)
    try:
        ai_reply = ask_ai(message.text)
    except Exception as e:
        ai_reply = "Sorry, I encountered an error talking to the AI service."
        print(f"AI Error: {e}", flush=True)
    bot.reply_to(message, ai_reply)


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    print("HANDLER TRIGGERED (photo)", flush=True)
    bot.reply_to(message, "📷 I received your photo, but I can't analyze images yet — only text. Feel free to describe what's in it and I'll help with that!")


@bot.message_handler(content_types=['document'])
def handle_document(message):
    print(f"HANDLER TRIGGERED (document): {message.document.file_name}", flush=True)
    bot.reply_to(message, f"📄 I received your file \"{message.document.file_name}\", but I can't read file contents yet — only text messages for now.")


@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    print("HANDLER TRIGGERED (voice)", flush=True)
    bot.reply_to(message, "🎤 I received your voice message, but I can't transcribe audio yet — only text for now.")


@bot.message_handler(content_types=['video', 'video_note'])
def handle_video(message):
    print("HANDLER TRIGGERED (video)", flush=True)
    bot.reply_to(message, "🎥 I received your video, but I can't analyze video yet — only text for now.")


@bot.message_handler(content_types=['sticker'])
def handle_sticker(message):
    print("HANDLER TRIGGERED (sticker)", flush=True)
    bot.reply_to(message, "😄 Nice sticker! I can only respond to text messages for now.")


@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    print("HANDLER TRIGGERED (audio)", flush=True)
    bot.reply_to(message, "🎵 I received your audio file, but I can't process audio yet — only text for now.")


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            update = telebot.types.Update.de_json(post_data.decode('utf-8'))
            bot.process_new_updates([update])

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        except Exception as e:
            print(f"WEBHOOK ERROR: {e}", flush=True)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Error logged')
