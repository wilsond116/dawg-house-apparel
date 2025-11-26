import os
from dotenv import load_dotenv
import requests
load_dotenv()
api_key = os.environ.get("TEXTBELT_API_KEY")
sender_name = 'dawghouseapprel.co@gmail.com'

def notify_owner(order):
    # Build the text message
    items = []
    for item in order.get("details", []):
        # Support both dict-based or list-based order storage
        if isinstance(item, dict):
            # Try to get product info cleanly
            name = item.get("name") or item.get("description") or "Unknown Item"
            qty = item.get("quantity", 1)
            items.append(f"{name} x{qty}")
        else:
            items.append(str(item))

    order_text = "\n".join(items) if items else "No items found."

    order_summary = (
        f"🐾 New Order Alert!\n"
        f"Customer: {order.get('name', 'N/A')}\n"
        f"Email: {order.get('email', 'N/A')}\n"
        f"Items:\n{order_text}\n"
        f"📦 Ship to: {order.get('address', 'N/A')}, "
        f"{order.get('city', '')}, {order.get('state', '')} {order.get('zip', '')}"
    )

    # Send text via Textbelt
    resp = requests.post("https://textbelt.com/text", {
        "phone": "5617139153",
        "message": order_summary,
        "key": api_key,
        "sender": sender_name,
    })
    print(resp.json())


