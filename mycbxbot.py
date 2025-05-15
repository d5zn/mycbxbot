import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# Загружаем переменные из кастомного .env
load_dotenv("tokens.env")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

NOTION_VERSION = "2022-06-28"

def parse_message(text):
    data = {}
    for line in text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data

def create_select(name):
    return {"name": name} if name else None

def create_multi_select(value):
    if not value:
        return []
    return [{"name": v.strip()} for v in value.split(",") if v.strip()]

def send_to_notion(data):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }

    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": data.get("Name", "")}}]},
            "Rating": {"number": float(data.get("Rating", 0))},
            "Brand": {"select": create_select(data.get("Brand", ""))},
            "Country": {"select": create_select(data.get("Country", ""))},
            "Region": {"multi_select": create_multi_select(data.get("Region", ""))},
            "Producer": {"select": create_select(data.get("Producer", ""))},
            "Altitude": {"rich_text": [{"text": {"content": data.get("Altitude", "")}}]},
            "Process": {"select": create_select(data.get("Process", ""))},
            "Roast Level": {"select": create_select(data.get("Roast Level", ""))},
            "Varietal": {"multi_select": create_multi_select(data.get("Varietal", ""))},
            "Flavor Notes": {"multi_select": create_multi_select(data.get("Flavor Notes", ""))},
            "Roasted": {"select": create_select(data.get("Roasted", ""))}
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    print("Status:", response.status_code)
    print("Response:", response.text)

def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    data = parse_message(text)
    try:
        send_to_notion(data)
        update.message.reply_text("✅ Данные отправлены в Notion!")
    except Exception as e:
        print("Ошибка:", e)
        update.message.reply_text("❌ Ошибка при отправке данных в Notion.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Бот запущен. Ожидает сообщения...")
    app.run_polling()