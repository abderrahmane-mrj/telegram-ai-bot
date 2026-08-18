import os
import telebot
import httpx
from http.server import BaseHTTPRequestHandler

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
INCEPTION_API_KEY = os.environ["INCEPTION_API_KEY"]

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(f"HANDLER TRIGGERED: {message.text}", flush=True)
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
        with httpx.Client(timeout=25) as client:
            response = client.post(
                "https://api.inceptionlabs.ai/v1/chat/completions",
                json=payload,
                headers=headers
            )
        print(f"AI Status: {response.status_code}", flush=True)
        response.raise_for_status()
        ai_reply = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        ai_reply = "Sorry, I encountered an error talking to the AI service."
        print(f"AI Error: {e}", flush=True)

    bot.reply_to(message, ai_reply)
    print("Reply sent", flush=True)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            print(f"RAW UPDATE: {post_data.decode('utf-8')}", flush=True)

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
