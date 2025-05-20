from flask import Flask
from telegram_bot import setup_bot

app = Flask(__name__)
bot, updater = setup_bot()

@app.route('/')
def index():
    return "Bot is running!"

if __name__ == '__main__':
    updater.start_polling()