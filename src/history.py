import os
from datetime import datetime
from collections import defaultdict
from src.saver import get_database_engine
import pandas as pd
from sqlalchemy import text

def get_order_history(filepath=None):
    """
    Read orders from PostgreSQL database and group orders by restaurant_name and date.
    Returns a list of grouped orders.
    """
    try:
        print("🔍 get_order_history() called - connecting to database...")
        engine = get_database_engine()
        print("✅ Database engine obtained")
        
        # Query only orders (where product is not null)
        # Order by date DESC for groups, but by id ASC within same date to preserve original order
        query = """
            SELECT 
                id,
                restaurant_id,
                restaurant_name,
                quantity,
                unit,
                product,
                corrections,
                date,
                original_text
            FROM restaurant_orders
            WHERE product IS NOT NULL AND product != ''
            ORDER BY date DESC, id ASC
        """
        
        print("📊 Executing SQL query...")
        df = pd.read_sql(query, engine)
        print(f"✅ Query completed - got {len(df)} rows")
        
        orders = []
        for _, row in df.iterrows():
            order_id = int(row.get("id")) if pd.notna(row.get("id")) else None
            restaurant_id = str(row.get("restaurant_id", "")) if pd.notna(row.get("restaurant_id")) else ""
            restaurant_name = str(row.get("restaurant_name", "")).strip() if pd.notna(row.get("restaurant_name")) else ""
            quantity = str(row.get("quantity", "")) if pd.notna(row.get("quantity")) else ""
            unit = str(row.get("unit", "")) if pd.notna(row.get("unit")) else ""
            product = str(row.get("product", "")).strip() if pd.notna(row.get("product")) else ""
            errors = str(row.get("corrections", "")) if pd.notna(row.get("corrections")) else ""
            date_value = row.get("date")
            
            # Skip rows without restaurant name or product
            if not restaurant_name or not product:
                continue
            
            # Parse date - handle TIMESTAMP format from database
            order_date = ""
            order_time = ""
            date_str = ""
            
            if pd.notna(date_value):
                if isinstance(date_value, datetime):
                    order_date = date_value.strftime("%d/%m/%Y")
                    order_time = date_value.strftime("%H:%M:%S")
                    date_str = date_value.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    date_str = str(date_value)
                    try:
                        # Try parsing as datetime string
                        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                        order_date = dt.strftime("%d/%m/%Y")
                        order_time = dt.strftime("%H:%M:%S")
                    except:
                        try:
                            dt = datetime.strptime(date_str, "%Y-%m-%d")
                            order_date = dt.strftime("%d/%m/%Y")
                            order_time = ""
                        except:
                            order_date = datetime.now().strftime("%d/%m/%Y")
                            order_time = ""
            else:
                order_date = datetime.now().strftime("%d/%m/%Y")
                order_time = ""
            
            # Extract original_text from database
            original_text = str(row.get("original_text", "")) if pd.notna(row.get("original_text")) else ""
            
            orders.append({
                "id": order_id,
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant_name,
                "quantity": quantity,
                "unit": unit,
                "product": product,
                "errors": errors,
                "date": order_date,
                "time": order_time,
                "datetime": date_str,
                "original_text": original_text
            })
        
        print(f"✅ Processed {len(orders)} orders from database")
    except Exception as e:
        print(f"⚠️  Error loading order history from database: {e}")
        import traceback
        traceback.print_exc()
        return []
    
    # Group orders by restaurant_name and date
    # Items are appended in the order they come from the database (ORDER BY id ASC)
    # This preserves the original text order: first item (lowest ID) first, last item (highest ID) last
    grouped = defaultdict(lambda: defaultdict(list))
    order_index = {}  # Track order of appearance for sorting (use last occurrence = most recent)
    
    for idx, order in enumerate(orders):
        key = (order["restaurant_name"], order["date"])
        # Use the first order's time for the group
        if key not in grouped or not grouped[key].get("time"):
            grouped[key]["restaurant_name"] = order["restaurant_name"]
            grouped[key]["restaurant_id"] = order["restaurant_id"]
            grouped[key]["date"] = order["date"]
            grouped[key]["time"] = order.get("time", "")
            grouped[key]["datetime"] = order.get("datetime", "")
        
        # Always update to the latest index (most recent order in the group)
        order_index[key] = idx
        
        # Append items in database order (id ASC), preserving original text order
        # First item texted = lower ID = appears first in list (top)
        # Last item texted = higher ID = appears last in list (bottom)
        grouped[key]["items"].append({
            "id": order.get("id"),
            "quantity": order["quantity"],
            "unit": order["unit"],
            "product": order["product"],
            "errors": order["errors"],
            "original_text": order.get("original_text", "")
        })
    
    # Convert to list format
    result = []
    for (restaurant_name, date), data in grouped.items():
        result.append({
            "restaurant_name": data["restaurant_name"],
            "restaurant_id": data["restaurant_id"],
            "date": data["date"],
            "time": data.get("time", ""),
            "datetime": data.get("datetime", ""),
            "items": data["items"],
            "_sort_index": order_index.get((restaurant_name, date), 0)
        })
    
    # Sort by date descending (newest first), then by order index (most recent first)
    # Convert dates to datetime for proper sorting
    def parse_date_for_sort(date_str):
        try:
            return datetime.strptime(date_str, "%d/%m/%Y")
        except:
            return datetime.now()
    
    def get_sort_key(order):
        # Try to parse full datetime if available
        dt = None
        if order.get("datetime"):
            try:
                # Try DD/MM/YYYY format
                dt = datetime.strptime(order["datetime"], "%d/%m/%Y")
            except:
                try:
                    # Try YYYY-MM-DD HH:MM:SS format
                    dt = datetime.strptime(order["datetime"], "%Y-%m-%d %H:%M:%S")
                except:
                    pass
        
        if dt is None:
            # Fallback to date
            dt = parse_date_for_sort(order["date"])
        
        # Return tuple: (datetime, sort_index) - higher index = more recent
        # reverse=True will sort by datetime descending, then by index descending
        return (dt, order.get("_sort_index", 0))
    
    # Sort by datetime (newest first), then by sort index (most recent first)
    print(f"🔄 Sorting {len(result)} grouped orders...")
    result.sort(key=get_sort_key, reverse=True)
    
    # Remove the sort index before returning
    for order in result:
        order.pop("_sort_index", None)
    
    print(f"✅ Returning {len(result)} grouped orders")
    return result

def get_messages(filepath=None):
    """
    Get all messages (non-order entries) from the database.
    Returns a list of messages sorted by most recent first.
    """
    try:
        engine = get_database_engine()
        
        # Query messages (where product is null or empty, and message is not null)
        query = """
            SELECT 
                id,
                restaurant_id,
                restaurant_name,
                date,
                corrections,
                need_attention,
                message
            FROM restaurant_orders
            WHERE (product IS NULL OR product = '')
                AND message IS NOT NULL AND message != ''
            ORDER BY date DESC
        """
        
        df = pd.read_sql(query, engine)
        
        messages = []
        for _, row in df.iterrows():
            message_id = int(row.get("id")) if pd.notna(row.get("id")) else None
            restaurant_id = str(row.get("restaurant_id", "")) if pd.notna(row.get("restaurant_id")) else ""
            restaurant_name = str(row.get("restaurant_name", "")).strip() if pd.notna(row.get("restaurant_name")) else ""
            date_value = row.get("date")
            corrections = str(row.get("corrections", "")) if pd.notna(row.get("corrections")) else ""
            need_attention_value = row.get("need_attention")
            message_text = str(row.get("message", "")).strip() if pd.notna(row.get("message")) else ""
            
            # Only include rows that have a message
            if not message_text:
                continue
                
            # Skip if no restaurant name
            if not restaurant_name:
                restaurant_name = "Unknown"
            
            # Determine need_attention flag
            need_attention_flag = "YES" if (pd.notna(need_attention_value) and bool(need_attention_value)) else "NO"
            
            # Parse date
            order_date = ""
            order_time = ""
            date_str = ""
            
            if pd.notna(date_value):
                if isinstance(date_value, datetime):
                    order_date = date_value.strftime("%d/%m/%Y")
                    order_time = date_value.strftime("%H:%M:%S")
                    date_str = date_value.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    date_str = str(date_value)
                    try:
                        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                        order_date = dt.strftime("%d/%m/%Y")
                        order_time = dt.strftime("%H:%M:%S")
                    except:
                        try:
                            dt = datetime.strptime(date_str, "%Y-%m-%d")
                            order_date = dt.strftime("%d/%m/%Y")
                            order_time = ""
                        except:
                            order_date = datetime.now().strftime("%d/%m/%Y")
                            order_time = ""
            else:
                order_date = datetime.now().strftime("%d/%m/%Y")
                order_time = ""
            
            messages.append({
                "id": message_id,
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant_name,
                "message": message_text,
                "date": order_date,
                "time": order_time,
                "datetime": date_str,
                "need_attention": need_attention_flag,
                "corrections": corrections,
                "read": False  # Can be extended later for read/unread functionality
            })
        
        # Sort by datetime (newest first)
        def parse_date_for_sort(date_str):
            if not date_str:
                return datetime.now()
            try:
                return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except:
                try:
                    return datetime.strptime(date_str, "%d/%m/%Y")
                except:
                    return datetime.now()
        
        messages.sort(key=lambda x: parse_date_for_sort(x["datetime"]), reverse=True)
        
        return messages
    except Exception as e:
        print(f"⚠️  Error loading messages from database: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_today_orders(filepath=None):
    """
    Get all orders from today only, grouped by restaurant name.
    Returns a list of grouped orders from today, sorted by most recent first.
    """
    try:
        engine = get_database_engine()
        
        # Get today's date for filtering
        today = datetime.now().date()
        
        # Query orders from today only (where product is not null)
        # Use SQLAlchemy text() for proper parameter handling
        # Order by date DESC for groups, but by id ASC within same date to preserve original order
        query = text("""
            SELECT 
                id,
                restaurant_id,
                restaurant_name,
                quantity,
                unit,
                product,
                corrections,
                date,
                original_text
            FROM restaurant_orders
            WHERE product IS NOT NULL AND product != ''
                AND DATE(date) = :today
            ORDER BY date DESC, id ASC
        """)
        
        df = pd.read_sql(query, engine, params={"today": today})
        
        orders = []
        for _, row in df.iterrows():
            order_id = int(row.get("id")) if pd.notna(row.get("id")) else None
            restaurant_id = str(row.get("restaurant_id", "")) if pd.notna(row.get("restaurant_id")) else ""
            restaurant_name = str(row.get("restaurant_name", "")).strip() if pd.notna(row.get("restaurant_name")) else ""
            quantity = str(row.get("quantity", "")) if pd.notna(row.get("quantity")) else ""
            unit = str(row.get("unit", "")) if pd.notna(row.get("unit")) else ""
            product = str(row.get("product", "")).strip() if pd.notna(row.get("product")) else ""
            errors = str(row.get("corrections", "")) if pd.notna(row.get("corrections")) else ""
            date_value = row.get("date")
            raw_message = str(row.get("original_text", "")) if pd.notna(row.get("original_text")) else ""
            
            # Skip rows without restaurant name or product
            if not restaurant_name or not product:
                continue
            
            # Parse date
            order_date = ""
            order_time = ""
            date_str = ""
            
            if pd.notna(date_value):
                if isinstance(date_value, datetime):
                    order_date = date_value.strftime("%d/%m/%Y")
                    order_time = date_value.strftime("%H:%M:%S")
                    date_str = date_value.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    date_str = str(date_value)
                    try:
                        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                        order_date = dt.strftime("%d/%m/%Y")
                        order_time = dt.strftime("%H:%M:%S")
                    except:
                        try:
                            dt = datetime.strptime(date_str, "%Y-%m-%d")
                            order_date = dt.strftime("%d/%m/%Y")
                            order_time = ""
                        except:
                            order_date = datetime.now().strftime("%d/%m/%Y")
                            order_time = ""
            else:
                order_date = datetime.now().strftime("%d/%m/%Y")
                order_time = ""
            
            # Parse errors if they exist (semicolon-separated string)
            error_list = []
            if errors:
                error_list = [e.strip() for e in errors.split(";") if e.strip()]
            
            orders.append({
                "id": order_id,
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant_name,
                "quantity": quantity,
                "unit": unit,
                "product": product,
                "errors": error_list,
                "date": order_date,
                "time": order_time,
                "datetime": date_str,
                "raw_message": raw_message
            })
    except Exception as e:
        print(f"⚠️  Error loading today's orders from database: {e}")
        import traceback
        traceback.print_exc()
        return []
    
    # Group orders by restaurant_name
    # Items are appended in the order they come from the database (ORDER BY id ASC)
    # This preserves the original text order: first item (lowest ID) first, last item (highest ID) last
    grouped = defaultdict(lambda: defaultdict(list))
    order_index = {}  # Track order of appearance for sorting
    
    for idx, order in enumerate(orders):
        restaurant_name = order["restaurant_name"]
        
        # Use the first order's time for the group
        if restaurant_name not in grouped or not grouped[restaurant_name].get("time"):
            grouped[restaurant_name]["restaurant_name"] = order["restaurant_name"]
            grouped[restaurant_name]["restaurant_id"] = order["restaurant_id"]
            grouped[restaurant_name]["date"] = order["date"]
            grouped[restaurant_name]["time"] = order.get("time", "")
            grouped[restaurant_name]["datetime"] = order.get("datetime", "")
        
        # Always update to the latest index (most recent order in the group)
        order_index[restaurant_name] = idx
        
        # Append items in database order (id ASC), preserving original text order
        # First item texted = lower ID = appears first in list (top)
        # Last item texted = higher ID = appears last in list (bottom)
        grouped[restaurant_name]["items"].append({
            "id": order.get("id"),
            "quantity": order["quantity"],
            "unit": order["unit"],
            "product": order["product"],
            "errors": order["errors"],
            "raw_message": order.get("raw_message", "")
        })
    
    # Convert to list format
    result = []
    for restaurant_name, data in grouped.items():
        result.append({
            "restaurant_name": data["restaurant_name"],
            "restaurant_id": data["restaurant_id"],
            "date": data["date"],
            "time": data.get("time", ""),
            "datetime": data.get("datetime", ""),
            "items": data["items"],
            "_sort_index": order_index.get(restaurant_name, 0)
        })
    
    # Sort by datetime (most recent first)
    def get_sort_datetime(order):
        if order.get("datetime"):
            try:
                # Try DD/MM/YYYY format
                return datetime.strptime(order["datetime"], "%d/%m/%Y")
            except:
                try:
                    # Try YYYY-MM-DD HH:MM:SS format
                    return datetime.strptime(order["datetime"], "%Y-%m-%d %H:%M:%S")
                except:
                    pass
        
        # Fallback to date only
        try:
            return datetime.strptime(order["date"], "%d/%m/%Y")
        except:
            return datetime.now()
    
    def get_sort_key(order):
        dt = get_sort_datetime(order)
        return (dt, order.get("_sort_index", 0))
    
    # Sort by datetime descending (newest first), then by sort index
    result.sort(key=get_sort_key, reverse=True)
    
    # Remove the sort index before returning
    for order in result:
        order.pop("_sort_index", None)
    
    return result
