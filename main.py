from flask import Flask
from telegram_bot import setup_bot
import asyncio

app = Flask(__name__)
telegram_app = setup_bot()

@app.route('/')
def index():
    return "Bot is running!"

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(telegram_app.run_polling())
    app.run(host='0.0.0.0', port=10000)
