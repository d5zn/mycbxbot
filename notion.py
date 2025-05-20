import os
from notion_client import Client

def get_notion_client():
    notion_token = os.getenv("NOTION_TOKEN")
    if not notion_token:
        raise ValueError("NOTION_TOKEN не задан")
    return Client(auth=notion_token)

def add_entry_to_notion(data):
    notion = get_notion_client()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
if not NOTION_TOKEN:
    raise ValueError("Переменная окружения NOTION_TOKEN не задана")
DATABASE_ID = os.environ["NOTION_DB_ID"]

notion = Client(auth=NOTION_TOKEN)

def create_select_or_add(option, prop_type="select"):
    if not option:
        return None
    return {"name": option}

def create_multi_select_or_add(options):
    return [{"name": o} for o in options if o]

def add_entry_to_notion(data):
    notion.pages.create(
        parent={"database_id": DATABASE_ID},
        properties={
            "Name": {"title": [{"text": {"content": data["Name"]}}]},
            "Rating": {"number": data["Rating"]},
            "Brand": {"select": create_select_or_add(data["Brand"])},
            "Country": {"select": create_select_or_add(data["Country"])},
            "Region": {"multi_select": create_multi_select_or_add(data["Region"])},
            "Producer": {"select": create_select_or_add(data["Producer"])},
            "Altitude": {"rich_text": [{"text": {"content": data["Altitude"]}}]},
            "Process": {"select": create_select_or_add(data["Process"])},
            "Roast Level": {"select": create_select_or_add(data["Roast Level"])},
            "Varietal": {"multi_select": create_multi_select_or_add(data["Varietal"])},
            "Flavor Notes": {"multi_select": create_multi_select_or_add(data["Flavor Notes"])},
            "Roasted": {"select": create_select_or_add(data["Roasted"])},
        }
    )
