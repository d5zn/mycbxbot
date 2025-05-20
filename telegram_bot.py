import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from notion import add_entry_to_notion

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]

user_state = {}

def setup_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
    return app, app

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_state[update.effective_user.id] = {}
    await update.message.reply_text("Привет! Введи данные в формате: Name, Rating, Brand, ...")

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    try:
        fields = [s.strip() for s in text.split(",")]
        if len(fields) < 12:
            await update.message.reply_text("Недостаточно данных. Нужно 12 полей.")
            return

        data = {
            "Name": fields[0],
            "Rating": int(fields[1]),
            "Brand": fields[2],
            "Country": fields[3],
            "Region": [r.strip() for r in fields[4].split(";")],
            "Producer": fields[5],
            "Altitude": fields[6],
            "Process": fields[7],
            "Roast Level": fields[8],
            "Varietal": [v.strip() for v in fields[9].split(";")],
            "Flavor Notes": [f.strip() for f in fields[10].split(";")],
            "Roasted": fields[11],
        }

        add_entry_to_notion(data)
        await update.message.reply_text("Запись добавлена в Notion!")

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")