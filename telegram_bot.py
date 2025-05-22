import os
from urllib.parse import quote
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from notion import add_entry_to_notion, get_page_data, update_entry_in_notion

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BOT_USERNAME = "mycbxbot"  # <= замените на username бота без @

if not TELEGRAM_TOKEN:
    raise ValueError("Переменная окружения TELEGRAM_TOKEN не задана")

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

TEMPLATE_MESSAGE = """Name: 
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
Roasted: """

def get_draft_template_url():
    encoded = quote(TEMPLATE_MESSAGE)
    return f"https://t.me/{BOT_USERNAME}?startapp={encoded}"

user_last_page = {}  # user_id -> page_id

def setup_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
    app.add_handler(CallbackQueryHandler(handle_callback))
    return app

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("✏️ Заполнить шаблон", url=get_draft_template_url())]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "Привет! Ты можешь отправить данные вручную, либо нажать кнопку ниже — и Telegram сразу вставит шаблон в поле ввода.",
        reply_markup=reply_markup
    )

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not text or ":" not in text:
        await update.message.reply_text("⚠️ Неверный формат. Используй Поле: значение")
        return

    user_id = update.effective_user.id
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

        if user_id in user_last_page and context.user_data.get("editing", False):
            page_id = user_last_page[user_id]
            update_entry_in_notion(page_id, data)
            await update.message.reply_text("✅ Запись обновлена в Notion!")
            context.user_data["editing"] = False
        else:
            page_id = add_entry_to_notion(data)
            user_last_page[user_id] = page_id
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔁 Редактировать", callback_data="edit_last")]
            ])
            await update.message.reply_text("✅ Запись добавлена в Notion!", reply_markup=keyboard)

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    page_id = user_last_page.get(user_id)

    if not page_id:
        await query.message.reply_text("❌ Не удалось найти запись.")
        return

    try:
        page_data = get_page_data(page_id)
        text_lines = []
        for key in FIELD_ALIASES:
            value = page_data.get(key)
            if isinstance(value, list):
                line = f"{key}: {', '.join(value)}"
            elif value:
                line = f"{key}: {value}"
            else:
                line = f"{key}:"
            text_lines.append(line)

        template = "\n".join(text_lines)
        context.user_data["editing"] = True

        await query.message.reply_text(
            "✏️ Вот текущая запись. Отредактируй и отправь заново:\n\n" + template
        )

    except Exception as e:
        await query.message.reply_text(f"❌ Ошибка при получении записи: {str(e)}")
