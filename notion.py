import os
from notion_client import Client

def get_notion_client():
    token = os.getenv("NOTION_TOKEN")
    if not token:
        raise ValueError("Переменная окружения NOTION_TOKEN не задана")
    return Client(auth=token)

def add_entry_to_notion(data):
    notion = get_notion_client()

    database_id = os.getenv("NOTION_DB_ID")
    if not database_id:
        raise ValueError("Переменная окружения NOTION_DB_ID не задана")

    notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Name": {"title": [{"text": {"content": data["Name"]}}]},
            "Rating": {"number": data["Rating"]},
            "Brand": {"select": {"name": data["Brand"]}},
            "Country": {"select": {"name": data["Country"]}},
            "Region": {"multi_select": [{"name": r} for r in data["Region"]]},
            "Producer": {"select": {"name": data["Producer"]}},
            "Altitude": {"rich_text": [{"text": {"content": data["Altitude"]}}]},
            "Process": {"select": {"name": data["Process"]}},
            "Roast Level": {"select": {"name": data["Roast Level"]}},
            "Varietal": {"multi_select": [{"name": v} for v in data["Varietal"]]},
            "Flavor Notes": {"multi_select": [{"name": f} for f in data["Flavor Notes"]]},
            "Roasted": {"select": {"name": data["Roasted"]}},
        }
    )
