import os
from telegram import Update, ReplyKeyboardMarkup
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

# Названия полей и поддержка мультивыбора
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

# Шаблон для вставки
TEMPLATE_MESSAGE = """\
Name: 
Rating: 
Brand: 
Country: 
Region: 
Producer: 
Altitude: 
Process: 
Roast Level: 
Varietal: 
Flavor Notes: 
Roasted: 
"""

def setup_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
    return app

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["📋 Вставить шаблон"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет! Отправь данные в формате:\n\n"
        "Поле: значение (одна строка — одно поле)\n"
        "Например:\n"
        "Name: Ethiopia Yirgacheffe\nRating: 87\n...\n\n"
        "Или нажми кнопку, чтобы вставить шаблон 👇",
        reply_markup=reply_markup
    )

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Кнопка "Вставить шаблон"
    if text == "📋 Вставить шаблон":
        await update.message.reply_text(
            TEMPLATE_MESSAGE,
            reply_markup=None  # Убираем клавиатуру
        )
        return

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
                try:
                    data[field] = float(value)
                except ValueError:
                    await update.message.reply_text("⚠️ Rating должен быть числом.")
                    return
            else:
                data[field] = value

        if not data:
            await update.message.reply_text("⚠️ Не удалось распознать ни одно поле.")
            return

        add_entry_to_notion(data)
        await update.message.reply_text("✅ Запись добавлена в Notion!")

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")
