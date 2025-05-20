import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from notion import add_entry_to_notion

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("Переменная окружения TELEGRAM_TOKEN не задана")

def setup_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
    return app

FIELD_ALIASES = {
    "Name": "Name",
    "Rating": "Rating",
    "Brand": "Brand",
    "Country": "Country",
    "Region": "Region",
    "Producer": "Producer",
    "Altitude": "Altitude",
    "Process": "Process",
    "Roast Level": "Roast Level",
    "Varietal": "Varietal",
    "Flavor Notes": "Flavor Notes",
    "Roasted": "Roasted",
}

MULTI_FIELDS = {"Region", "Varietal", "Flavor Notes"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь данные в таком формате (одна строка — одно поле):\n\n"
        "Name: Test Coffee\nRating: 87\nBrand: Sample Roasters\n...\n\n"
        "Для множественных значений используй запятую: Flavor Notes: Citrus, Floral"
    )

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    lines = text.splitlines()
    data = {}

    try:
        for line in lines:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            field = FIELD_ALIASES.get(key)
            if not field or not value:
                continue

            if field in MULTI_FIELDS:
                data[field] = [v.strip() for v in value.split(",") if v.strip()]
            elif field == "Rating":
                data[field] = float(value)
            else:
                data[field] = value

        if not data:
            await update.message.reply_text("⚠️ Не удалось распознать ни одно поле.")
            return

        add_entry_to_notion(data)
        await update.message.reply_text("✅ Запись добавлена в Notion!")

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")
