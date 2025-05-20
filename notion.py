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

    def safe_select(name):
        return {"name": name} if name else None

    def safe_multi(name_list):
        return [{"name": v} for v in name_list] if name_list else []

    props = {}

    if "Name" in data:
        props["Name"] = {"title": [{"text": {"content": data["Name"]}}]}
    if "Rating" in data:
        props["Rating"] = {"number": data["Rating"]}
    if "Brand" in data:
        props["Brand"] = {"select": safe_select(data["Brand"])}
    if "Country" in data:
        props["Country"] = {"select": safe_select(data["Country"])}
    if "Region" in data:
        props["Region"] = {"multi_select": safe_multi(data["Region"])}
    if "Producer" in data:
        props["Producer"] = {"select": safe_select(data["Producer"])}
    if "Altitude" in data:
        props["Altitude"] = {"rich_text": [{"text": {"content": data["Altitude"]}}]}
    if "Process" in data:
        props["Process"] = {"select": safe_select(data["Process"])}
    if "Roast Level" in data:
        props["Roast Level"] = {"select": safe_select(data["Roast Level"])}
    if "Varietal" in data:
        props["Varietal"] = {"multi_select": safe_multi(data["Varietal"])}
    if "Flavor Notes" in data:
        props["Flavor Notes"] = {"multi_select": safe_multi(data["Flavor Notes"])}
    if "Roasted" in data:
        props["Roasted"] = {"select": safe_select(data["Roasted"])}

    notion.pages.create(
        parent={"database_id": database_id},
        properties=props
    )
