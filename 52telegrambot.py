import telebot
import requests
from flask import Flask
import threading
import os
import time

# ====== توکن ربات ======
TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

# ====== handler های ربات ======
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how can I help you?")

@bot.message_handler(func=lambda m: True)
def show_price(message):
    symbol = message.text.upper()
    if not symbol.endswith("USDT"):
        symbol = symbol + "USDT"
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        bot.reply_to(message, f"{data['symbol']} is {data['price']}")
    else:
        bot.reply_to(message, "something went wrong")

# ====== اجرای ربات با مدیریت خطای 409 ======
def run_bot():
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except telebot.apihelper.ApiTelegramException as e:
            if "409" in str(e):
                print("⚠️ Conflict: bot already running somewhere. Retrying in 5 seconds...")
                time.sleep(5)
            else:
                raise e
        except Exception as e:
            print("⚠️ Unexpected error:", e)
            time.sleep(5)

threading.Thread(target=run_bot).start()

# ====== سرور Flask برای Render ======
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)
