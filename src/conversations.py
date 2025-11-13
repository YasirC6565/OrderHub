from datetime import datetime
from collections import defaultdict
from src.saver import get_database_engine
import pandas as pd


def get_all_conversations(filepath=None):
    """
    Get all conversations grouped by restaurant from the database.
    Groups messages/orders by timestamp (same date and time) and combines raw messages.
    Includes replies (outgoing messages) from conversations table.
    Returns a list of restaurants with their message/order history.
    Corrections are removed from the output.
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
        
        # Also query replies (outgoing messages) from conversations table
        try:
            conversations_query = """
                SELECT 
                    restaurant_id,
                    restaurant_name,
                    message,
                    direction,
                    parent_message_id,
                    created_at
                FROM conversations
                WHERE direction = 'outgoing'
                ORDER BY created_at DESC
            """
            df_conversations = pd.read_sql(conversations_query, engine)
        except Exception as e:
            print(f"⚠️  Could not load conversations table (may not exist yet): {e}")
            df_conversations = pd.DataFrame()
        
        # First pass: collect all rows and group by (restaurant_name, timestamp)
        # Use a more precise timestamp key (rounded to seconds for grouping)
        timestamp_groups = defaultdict(list)
        
        for _, row in df.iterrows():
            restaurant_id = str(row.get("restaurant_id", "")) if pd.notna(row.get("restaurant_id")) else ""
            restaurant_name = str(row.get("restaurant_name", "")).strip() if pd.notna(row.get("restaurant_name")) else ""
            quantity = str(row.get("quantity", "")) if pd.notna(row.get("quantity")) else ""
            unit = str(row.get("unit", "")) if pd.notna(row.get("unit")) else ""
            product = str(row.get("product", "")).strip() if pd.notna(row.get("product")) else ""
            date_value = row.get("date")
            original_text = str(row.get("original_text", "")) if pd.notna(row.get("original_text")) else ""
            message_text = str(row.get("message", "")).strip() if pd.notna(row.get("message")) else ""
            
            # Skip if no restaurant name
            if not restaurant_name:
                continue
            
            # Parse date and create timestamp key (rounded to seconds)
            formatted_date = ""
            date_str = ""
            timestamp = 0
            timestamp_key = None  # Key for grouping: (restaurant_name, rounded_timestamp)
            
            if pd.notna(date_value):
                if isinstance(date_value, datetime):
                    formatted_date = date_value.strftime("%d/%m/%Y")
                    date_str = date_value.strftime("%Y-%m-%d %H:%M:%S")
                    timestamp = date_value.timestamp()
                    # Round to seconds for grouping (same second = same message)
                    timestamp_key = (restaurant_name, int(timestamp))
                else:
                    date_str = str(date_value)
                    try:
                        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                        formatted_date = dt.strftime("%d/%m/%Y")
                        timestamp = dt.timestamp()
                        timestamp_key = (restaurant_name, int(timestamp))
                    except:
                        try:
                            dt = datetime.strptime(date_str, "%Y-%m-%d")
                            formatted_date = dt.strftime("%d/%m/%Y")
                            timestamp = dt.timestamp()
                            timestamp_key = (restaurant_name, int(timestamp))
                        except:
                            formatted_date = datetime.now().strftime("%d/%m/%Y")
                            timestamp = 0
                            timestamp_key = (restaurant_name, int(datetime.now().timestamp()))
            else:
                formatted_date = datetime.now().strftime("%d/%m/%Y")
                timestamp = 0
                timestamp_key = (restaurant_name, int(datetime.now().timestamp()))
            
            # Store row data for grouping
            timestamp_groups[timestamp_key].append({
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant_name,
                "quantity": quantity,
                "unit": unit,
                "product": product,
                "original_text": original_text,
                "message_text": message_text,
                "formatted_date": formatted_date,
                "date_str": date_str,
                "timestamp": timestamp
            })
        
        # Add outgoing messages (replies) from conversations table
        if not df_conversations.empty:
            for _, row in df_conversations.iterrows():
                restaurant_id = str(row.get("restaurant_id", "")) if pd.notna(row.get("restaurant_id")) else ""
                restaurant_name = str(row.get("restaurant_name", "")).strip() if pd.notna(row.get("restaurant_name")) else ""
                message_text = str(row.get("message", "")).strip() if pd.notna(row.get("message")) else ""
                created_at = row.get("created_at")
                
                if not restaurant_name or not message_text:
                    continue
                
                # Parse created_at timestamp
                formatted_date = ""
                date_str = ""
                timestamp = 0
                
                if pd.notna(created_at):
                    if isinstance(created_at, datetime):
                        formatted_date = created_at.strftime("%d/%m/%Y")
                        date_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
                        timestamp = created_at.timestamp()
                    else:
                        date_str = str(created_at)
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
                                timestamp = datetime.now().timestamp()
                else:
                    formatted_date = datetime.now().strftime("%d/%m/%Y")
                    timestamp = datetime.now().timestamp()
                
                # Create a unique timestamp key for this reply
                timestamp_key = (restaurant_name, int(timestamp))
                
                # Add reply as a separate message entry
                timestamp_groups[timestamp_key].append({
                    "restaurant_id": restaurant_id,
                    "restaurant_name": restaurant_name,
                    "quantity": "",
                    "unit": "",
                    "product": "",
                    "original_text": "",
                    "message_text": message_text,
                    "formatted_date": formatted_date,
                    "date_str": date_str,
                    "timestamp": timestamp,
                    "direction": "outgoing"  # Mark as outgoing
                })
        
        # Second pass: group by restaurant and combine messages with same timestamp
        conversations = defaultdict(list)
        
        for (restaurant_name, _), rows in timestamp_groups.items():
            # Combine original_text from all rows with same timestamp
            all_texts = []
            has_order = False
            
            # Get metadata from first row (they all have same timestamp)
            first_row = rows[0]
            restaurant_id = first_row["restaurant_id"]
            formatted_date = first_row["formatted_date"]
            date_str = first_row["date_str"]
            timestamp = first_row["timestamp"]
            
            for row in rows:
                # For outgoing messages (replies), prioritize message_text
                if row.get("direction") == "outgoing" and row["message_text"] and row["message_text"].strip():
                    all_texts.append(row["message_text"].strip())
                # For incoming messages, prioritize original_text (raw message) over formatted text
                elif row["original_text"] and row["original_text"].strip():
                    all_texts.append(row["original_text"].strip())
                elif row["message_text"] and row["message_text"].strip():
                    # Fallback to message_text if original_text is not available
                    all_texts.append(row["message_text"].strip())
                elif row["product"]:
                    # Fallback to formatted order if neither original_text nor message_text available
                    order_text = f"{row['quantity']} {row['unit']} {row['product']}".strip()
                    if order_text:
                        all_texts.append(order_text)
                
                # Check if any row has a product (order)
                if row["product"]:
                    has_order = True
            
            # Check if this is an outgoing message (reply)
            is_outgoing = any(row.get("direction") == "outgoing" for row in rows)
            
            # Combine all texts with newlines (this creates the raw message format)
            if all_texts:
                combined_content = "\n".join(all_texts)
                
                # Determine type: if it has product, it's an order, otherwise it's a message
                msg_type = "order" if has_order else "message"
                
                # Add to conversations (no corrections field)
                # Default to "incoming" if direction is not specified
                direction = "outgoing" if is_outgoing else "incoming"
                
                conversations[restaurant_name].append({
                    "type": msg_type,
                    "content": combined_content,
                    "date": formatted_date,
                    "datetime": date_str,
                    "timestamp": timestamp,
                    "restaurant_id": restaurant_id,
                    "direction": direction  # Add direction field
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

