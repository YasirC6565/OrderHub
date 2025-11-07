import csv
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Get the project root directory (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

def get_order_history(filepath="orders.csv"):
    """
    Read orders.csv and group orders by restaurant_name and date.
    Uses the header row to understand the database structure.
    Returns a list of grouped orders.
    """
    if not os.path.isabs(filepath):
        filepath = PROJECT_ROOT / filepath
    filepath = str(filepath)
    
    if not os.path.isfile(filepath):
        return []
    
    orders = []
    
    # Use csv.DictReader to properly parse using header row
    with open(filepath, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        # The header row will be automatically skipped by DictReader
        # Column names from header: restaurent_id, restaurent_name, quantity, unit, product, corrections , date, original text
        
        for row in reader:
            # Get values using the actual column names from header (note: typo in header "restaurent")
            restaurant_id = row.get("restaurent_id", row.get("restaurant_id", "")).strip()
            restaurant_name = row.get("restaurent_name", row.get("restaurant_name", "")).strip()
            quantity = row.get("quantity", "").strip()
            unit = row.get("unit", "").strip()
            product = row.get("product", "").strip()
            errors = row.get("corrections ", row.get("corrections", "")).strip()  # Note: space after "corrections " in header
            date_str = row.get("date", "").strip()
            
            # Skip rows without restaurant name or product
            if not restaurant_name or not product:
                continue
            
            # Skip separator/divider rows
            if restaurant_name in ["---", "------", "----------", "------------------", "----------------", "-------------------", "---------------------", "----------------------", "----------------------------", "---------------------------", "------------------------", "--------------------------", "--------------------------------------"]:
                continue
            
            # Parse date - handle DD/MM/YYYY format (UK format)
            order_date = ""
            order_time = ""
            
            if date_str:
                try:
                    # Try DD/MM/YYYY format first (UK format)
                    order_datetime = datetime.strptime(date_str, "%d/%m/%Y")
                    order_date = order_datetime.strftime("%d/%m/%Y")  # Keep UK format
                    order_time = ""  # No time in this format
                except:
                    try:
                        # Try YYYY-MM-DD HH:MM:SS format
                        order_datetime = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                        order_date = order_datetime.strftime("%d/%m/%Y")  # Convert to UK format
                        order_time = order_datetime.strftime("%H:%M:%S")
                    except:
                        # Fallback - try to extract date parts
                        parts = date_str.split()
                        if "/" in parts[0]:
                            # DD/MM/YYYY format - keep as is
                            order_date = parts[0]
                        else:
                            # Try to convert YYYY-MM-DD to DD/MM/YYYY
                            try:
                                d = datetime.strptime(parts[0], "%Y-%m-%d")
                                order_date = d.strftime("%d/%m/%Y")
                            except:
                                order_date = datetime.now().strftime("%d/%m/%Y")
                        order_time = parts[1] if len(parts) > 1 else ""
            else:
                # No date - use current date for grouping in UK format
                order_date = datetime.now().strftime("%d/%m/%Y")
                order_time = ""
            
            orders.append({
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant_name,
                "quantity": quantity,
                "unit": unit,
                "product": product,
                "errors": errors,
                "date": order_date,
                "time": order_time,
                "datetime": date_str
            })
    
    # Group orders by restaurant_name and date
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
        
        grouped[key]["items"].append({
            "quantity": order["quantity"],
            "unit": order["unit"],
            "product": order["product"],
            "errors": order["errors"]
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
    result.sort(key=get_sort_key, reverse=True)
    
    # Remove the sort index before returning
    for order in result:
        order.pop("_sort_index", None)
    
    return result

def get_today_orders(filepath="orders.csv"):
    """
    Get all orders from today only, grouped by restaurant name.
    Returns a list of grouped orders from today, sorted by most recent first.
    """
    if not os.path.isabs(filepath):
        filepath = PROJECT_ROOT / filepath
    filepath = str(filepath)
    
    if not os.path.isfile(filepath):
        return []
    
    # Get today's date in UK format
    today = datetime.now().strftime("%d/%m/%Y")
    
    orders = []
    
    # Use csv.DictReader to properly parse using header row
    with open(filepath, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            restaurant_id = row.get("restaurent_id", row.get("restaurant_id", "")).strip()
            restaurant_name = row.get("restaurent_name", row.get("restaurant_name", "")).strip()
            quantity = row.get("quantity", "").strip()
            unit = row.get("unit", "").strip()
            product = row.get("product", "").strip()
            errors = row.get("corrections ", row.get("corrections", "")).strip()
            date_str = row.get("date", "").strip()
            raw_message = row.get("original text", row.get("original_text", "")).strip()
            
            # Skip rows without restaurant name or product
            if not restaurant_name or not product:
                continue
            
            # Skip separator/divider rows
            if restaurant_name in ["---", "------", "----------", "------------------", "----------------", "-------------------", "---------------------", "----------------------", "----------------------------", "---------------------------", "------------------------", "--------------------------", "--------------------------------------"]:
                continue
            
            # Parse date and check if it's today
            order_date = ""
            order_time = ""
            
            if date_str:
                try:
                    # Try DD/MM/YYYY format first (UK format)
                    order_datetime = datetime.strptime(date_str, "%d/%m/%Y")
                    order_date = order_datetime.strftime("%d/%m/%Y")
                    order_time = ""
                except:
                    try:
                        # Try YYYY-MM-DD HH:MM:SS format
                        order_datetime = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                        order_date = order_datetime.strftime("%d/%m/%Y")
                        order_time = order_datetime.strftime("%H:%M:%S")
                    except:
                        # Fallback
                        parts = date_str.split()
                        if "/" in parts[0]:
                            order_date = parts[0]
                        else:
                            try:
                                d = datetime.strptime(parts[0], "%Y-%m-%d")
                                order_date = d.strftime("%d/%m/%Y")
                            except:
                                order_date = datetime.now().strftime("%d/%m/%Y")
                        order_time = parts[1] if len(parts) > 1 else ""
            else:
                # No date - use current date
                order_date = datetime.now().strftime("%d/%m/%Y")
                order_time = ""
            
            # Only include orders from today
            if order_date == today:
                # Parse errors if they exist (semicolon-separated string)
                error_list = []
                if errors:
                    error_list = [e.strip() for e in errors.split(";") if e.strip()]
                
                orders.append({
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
    
    # Group orders by restaurant_name
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
        
        grouped[restaurant_name]["items"].append({
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
