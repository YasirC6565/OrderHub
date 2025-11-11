import csv
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Get the project root directory (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()


def get_all_conversations(filepath="orders.csv"):
    """
    Get all conversations grouped by restaurant.
    Returns a list of restaurants with their message/order history.
    """
    if not os.path.isabs(filepath):
        filepath = PROJECT_ROOT / filepath
    filepath = str(filepath)
    
    if not os.path.isfile(filepath):
        return []
    
    # Group messages by restaurant
    conversations = defaultdict(list)
    
    with open(filepath, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            restaurant_id = row.get("restaurent_id", row.get("restaurant_id", "")).strip()
            restaurant_name = row.get("restaurent_name", row.get("restaurant_name", "")).strip()
            quantity = row.get("quantity", "").strip()
            unit = row.get("unit", "").strip()
            product = row.get("product", "").strip()
            corrections = row.get("corrections ", row.get("corrections", "")).strip()
            date_str = row.get("date", "").strip()
            original_text = row.get("original text", row.get("original_text", "")).strip()
            message_text = row.get("Message", "").strip()
            
            # Skip if no restaurant name
            if not restaurant_name:
                continue
            
            # Parse date
            try:
                dt = datetime.strptime(date_str, "%d/%m/%Y")
                formatted_date = dt.strftime("%d/%m/%Y")
                timestamp = dt.timestamp()
            except:
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    formatted_date = dt.strftime("%d/%m/%Y")
                    timestamp = dt.timestamp()
                except:
                    formatted_date = date_str
                    timestamp = 0
            
            # Determine message type and content
            if message_text:
                # It's a natural message
                conversations[restaurant_name].append({
                    "type": "message",
                    "content": message_text,
                    "date": formatted_date,
                    "datetime": date_str,
                    "timestamp": timestamp,
                    "corrections": corrections,
                    "restaurant_id": restaurant_id
                })
            elif product:
                # It's an order
                order_text = original_text if original_text else f"{quantity} {unit} {product}".strip()
                conversations[restaurant_name].append({
                    "type": "order",
                    "content": order_text,
                    "quantity": quantity,
                    "unit": unit,
                    "product": product,
                    "date": formatted_date,
                    "datetime": date_str,
                    "timestamp": timestamp,
                    "corrections": corrections,
                    "restaurant_id": restaurant_id
                })
    
    # Convert to list format with last message info
    result = []
    for restaurant_name, messages in conversations.items():
        # Sort messages by timestamp (oldest first for display)
        messages.sort(key=lambda x: x.get("timestamp", 0))
        
        # Get last message for preview
        last_message = messages[-1] if messages else None
        last_message_preview = ""
        last_message_date = ""
        
        if last_message:
            if last_message["type"] == "message":
                last_message_preview = last_message["content"][:50]
            else:
                last_message_preview = f"Order: {last_message['content'][:40]}"
            last_message_date = last_message["date"]
        
        result.append({
            "restaurant_name": restaurant_name,
            "restaurant_id": messages[0]["restaurant_id"] if messages else "",
            "messages": messages,
            "message_count": len(messages),
            "last_message": last_message_preview,
            "last_message_date": last_message_date,
            "last_timestamp": messages[-1]["timestamp"] if messages else 0
        })
    
    # Sort by last message timestamp (most recent first)
    result.sort(key=lambda x: x["last_timestamp"], reverse=True)
    
    return result

