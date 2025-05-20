from telegram_bot import setup_bot
import asyncio

if __name__ == '__main__':
    asyncio.run(setup_bot().run_polling())
