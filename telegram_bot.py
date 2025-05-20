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

FIELD_NAMES = [
    "Name", "Rating", "Brand", "Country", "Region",
    "Producer", "Altitude", "Process", "Roast Level",
    "Varietal", "Flavor Notes", "Roasted"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Введи до 12 полей, разделённых запятыми, в следующем порядке:\n\n"
        "Name, Rating, Brand, Country, Region1;Region2, Producer, Altitude, "
        "Process, Roast Level, Varietal1;Varietal2, FlavorNote1;FlavorNote2, Roasted\n\n"
        "Ты можешь отправить меньше — просто оставь неиспользуемые поля пустыми."
    )

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    parts = [s.strip() for s in text.split(",")]
    
    if not parts or all(p == "" for p in parts):
        await update.message.reply_text("⚠️ Невозможно обработать пустое сообщение.")
        return

    try:
        data = {}
        for i, value in enumerate(parts):
            if i >= len(FIELD_NAMES):
                break
            field_name = FIELD_NAMES[i]
            if value == "":
                continue  # пропускаем пустые
            if field_name in ["Region", "Varietal", "Flavor Notes"]:
                data[field_name] = [v.strip() for v in value.split(";") if v.strip()]
            elif field_name == "Rating":
                try:
                    data[field_name] = int(value)
                except ValueError:
                    await update.message.reply_text("⚠️ Rating должен быть числом.")
                    return
            else:
                data[field_name] = value

        add_entry_to_notion(data)
        await update.message.reply_text("✅ Запись добавлена в Notion!")

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")
