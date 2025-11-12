from datetime import datetime
from collections import defaultdict
from src.saver import get_database_engine
import pandas as pd


def get_all_conversations(filepath=None):
    """
    Get all conversations grouped by restaurant from the database.
    Returns a list of restaurants with their message/order history.
    """
    try:
        engine = get_database_engine()
        
        # Query all orders and messages from the database
        query = """
            SELECT 
                restaurant_id,
                restaurant_name,
                quantity,
                unit,
                product,
                corrections,
                date,
                original_text,
                message
            FROM restaurant_orders
            ORDER BY date DESC
        """
        
        df = pd.read_sql(query, engine)
        
        # Group messages by restaurant
        conversations = defaultdict(list)
        
        for _, row in df.iterrows():
            restaurant_id = str(row.get("restaurant_id", "")) if pd.notna(row.get("restaurant_id")) else ""
            restaurant_name = str(row.get("restaurant_name", "")).strip() if pd.notna(row.get("restaurant_name")) else ""
            quantity = str(row.get("quantity", "")) if pd.notna(row.get("quantity")) else ""
            unit = str(row.get("unit", "")) if pd.notna(row.get("unit")) else ""
            product = str(row.get("product", "")).strip() if pd.notna(row.get("product")) else ""
            corrections = str(row.get("corrections", "")) if pd.notna(row.get("corrections")) else ""
            date_value = row.get("date")
            original_text = str(row.get("original_text", "")) if pd.notna(row.get("original_text")) else ""
            message_text = str(row.get("message", "")).strip() if pd.notna(row.get("message")) else ""
            
            # Skip if no restaurant name
            if not restaurant_name:
                continue
            
            # Parse date
            formatted_date = ""
            date_str = ""
            timestamp = 0
            
            if pd.notna(date_value):
                if isinstance(date_value, datetime):
                    formatted_date = date_value.strftime("%d/%m/%Y")
                    date_str = date_value.strftime("%Y-%m-%d %H:%M:%S")
                    timestamp = date_value.timestamp()
                else:
                    date_str = str(date_value)
                    try:
                        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                        formatted_date = dt.strftime("%d/%m/%Y")
                        timestamp = dt.timestamp()
                    except:
                        try:
                            dt = datetime.strptime(date_str, "%Y-%m-%d")
                            formatted_date = dt.strftime("%d/%m/%Y")
                            timestamp = dt.timestamp()
                        except:
                            formatted_date = datetime.now().strftime("%d/%m/%Y")
                            timestamp = 0
            else:
                formatted_date = datetime.now().strftime("%d/%m/%Y")
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
    except Exception as e:
        print(f"⚠️  Error loading conversations from database: {e}")
        import traceback
        traceback.print_exc()
        return []
    
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

