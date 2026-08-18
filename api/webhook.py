import os
import telebot
import requests
from http.server import BaseHTTPRequestHandler

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
INCEPTION_API_KEY = os.environ["INCEPTION_API_KEY"]

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text

    headers = {
        "Authorization": f"Bearer {INCEPTION_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mercury-2",
        "reasoning_effort": "low",
        "messages": [{"role": "user", "content": user_text}]
    }

    try:
        response = requests.post(
            "https://api.inceptionlabs.ai/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=25
        )
        response.raise_for_status()
        ai_reply = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        ai_reply = "Sorry, I encountered an error talking to the AI service."
        print(f"Error: {e}")

    bot.reply_to(message, ai_reply)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        update = telebot.types.Update.de_json(post_data.decode('utf-8'))
        bot.process_new_updates([update])

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
