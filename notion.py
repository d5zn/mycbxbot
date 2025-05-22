import os
from notion_client import Client

def get_notion_client():
    token = os.getenv("NOTION_TOKEN")
    if not token:
        raise ValueError("NOTION_TOKEN не задан")
    return Client(auth=token)

def safe_select(name):
    return {"name": name} if name else None

def safe_multi(name_list):
    return [{"name": v} for v in name_list] if name_list else []

def add_entry_to_notion(data):
    notion = get_notion_client()
    database_id = os.getenv("NOTION_DB_ID")
    if not database_id:
        raise ValueError("NOTION_DB_ID не задан")

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

    page = notion.pages.create(
        parent={"database_id": database_id},
        properties=props
    )

    return page["id"]

def get_page_data(page_id):
    notion = get_notion_client()
    page = notion.pages.retrieve(page_id=page_id)
    properties = page["properties"]

    def extract_text(prop):
        if "title" in prop:
            return prop["title"][0]["text"]["content"] if prop["title"] else ""
        if "rich_text" in prop:
            return prop["rich_text"][0]["text"]["content"] if prop["rich_text"] else ""
        return ""

    def extract_select(prop):
        return prop["select"]["name"] if prop["select"] else ""

    def extract_multi(prop):
        return [item["name"] for item in prop["multi_select"]]

    def extract_number(prop):
        return str(prop["number"]) if prop["number"] is not None else ""

    data = {
        "Name": extract_text(properties.get("Name", {})),
        "Rating": extract_number(properties.get("Rating", {})),
        "Brand": extract_select(properties.get("Brand", {})),
        "Country": extract_select(properties.get("Country", {})),
        "Region": extract_multi(properties.get("Region", {})),
        "Producer": extract_select(properties.get("Producer", {})),
        "Altitude": extract_text(properties.get("Altitude", {})),
        "Process": extract_select(properties.get("Process", {})),
        "Roast Level": extract_select(properties.get("Roast Level", {})),
        "Varietal": extract_multi(properties.get("Varietal", {})),
        "Flavor Notes": extract_multi(properties.get("Flavor Notes", {})),
        "Roasted": extract_select(properties.get("Roasted", {})),
    }

    return data

def update_entry_in_notion(page_id, data):
    notion = get_notion_client()

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

    notion.pages.update(page_id=page_id, properties=props)
