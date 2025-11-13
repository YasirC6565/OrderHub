from src.parser import parser_order
from src.utils.special_cases import apply_special_cases
from src.validator import validate_order
from src.saver import save_order, save_message, save_to_conversations
from src.input_tool import input_text_tool
from src.db import get_products, get_restaurant_by_name, get_restaurant_by_phone
from src.alerts import send_manager_alert
from src.ai.order_parser import ai_parse_order, normalize_order
from src.ai.conversational_agent import conversational_agent, get_welcome_message
from src.history import get_order_history, get_today_orders, get_messages
from src.conversations import get_all_conversations
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from datetime import datetime
import os
load_dotenv()


app = FastAPI()

# Enable CORS for frontend connection
# Allow ONLY specific origins (no wildcard for security)
allowed_origins = [
    "https://order-hub-nine.vercel.app",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.get("/history")
def get_history():
    """Get order history grouped by restaurant and date"""
    try:
        print("📡 /history endpoint called")
        orders = get_order_history()
        print(f"✅ Found {len(orders)} orders")
        if orders:
            print(f"   First order: {orders[0].get('restaurant_name')} - {len(orders[0].get('items', []))} items")
        response_data = {"orders": orders}
        print(f"📤 Returning {len(orders)} orders to frontend")
        return response_data
    except Exception as e:
        print(f"❌ Error loading history: {e}")
        import traceback
        traceback.print_exc()
        return {"orders": [], "error": str(e)}

@app.get("/feed")
def get_feed():
    """Get today's orders for live feed"""
    try:
        orders = get_today_orders()
        return {"orders": orders, "date": datetime.now().strftime("%d/%m/%Y")}
    except Exception as e:
        print(f"Error loading feed: {e}")
        import traceback
        traceback.print_exc()
        return {"orders": [], "error": str(e), "date": datetime.now().strftime("%d/%m/%Y")}

@app.get("/messages")
def get_messages_endpoint():
    """Get all messages from restaurants"""
    try:
        messages = get_messages()
        return {"messages": messages, "count": len(messages)}
    except Exception as e:
        print(f"Error loading messages: {e}")
        import traceback
        traceback.print_exc()
        return {"messages": [], "count": 0, "error": str(e)}

@app.get("/conversations")
def get_conversations_endpoint():
    """Get all conversations grouped by restaurant"""
    try:
        conversations = get_all_conversations()
        return {"conversations": conversations, "count": len(conversations)}
    except Exception as e:
        print(f"Error loading conversations: {e}")
        import traceback
        traceback.print_exc()
        return {"conversations": [], "count": 0, "error": str(e)}

@app.delete("/order/group")
def delete_order_group(restaurant_name: str, date: str):
    """Delete all order items for a restaurant on a specific date"""
    try:
        from src.saver import get_database_engine
        from sqlalchemy import text
        
        engine = get_database_engine()
        
        # Parse date from DD/MM/YYYY format
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date, "%d/%m/%Y").date()
        except:
            return {"status": "error", "message": "Invalid date format. Use DD/MM/YYYY"}
        
        # Delete all order items for this restaurant and date
        query = text("""
            DELETE FROM restaurant_orders 
            WHERE restaurant_name = :restaurant_name 
            AND DATE(date) = :date
            AND product IS NOT NULL AND product != ''
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {"restaurant_name": restaurant_name, "date": date_obj})
            conn.commit()
            
        if result.rowcount > 0:
            return {"status": "deleted", "message": f"Deleted {result.rowcount} order item(s) for {restaurant_name} on {date}"}
        else:
            return {"status": "not_found", "message": f"No orders found for {restaurant_name} on {date}"}
    except Exception as e:
        print(f"Error deleting order group: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.delete("/order/{order_id}")
def delete_order_item(order_id: int):
    """Delete a single order item by ID"""
    try:
        from src.saver import get_database_engine
        from sqlalchemy import text
        
        engine = get_database_engine()
        
        # Delete the order item
        query = text("DELETE FROM restaurant_orders WHERE id = :order_id")
        with engine.connect() as conn:
            result = conn.execute(query, {"order_id": order_id})
            conn.commit()
            
        if result.rowcount > 0:
            return {"status": "deleted", "message": f"Order item {order_id} deleted successfully"}
        else:
            return {"status": "not_found", "message": f"Order item {order_id} not found"}
    except Exception as e:
        print(f"Error deleting order item: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.get("/welcome/{restaurant_name}")
def get_welcome(restaurant_name: str):
    """Get welcome message for a restaurant"""
    return {
        "message": get_welcome_message(restaurant_name, "today"),
        "restaurant_name": restaurant_name
    }

@app.get("/whatsapp")
def whatsapp_health():
    return {"status": "ok"}

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    sender = form.get("From")
    body = form.get("Body")
    restaurant_name_input = form.get("RestaurantName")

    # 🔑 Lookup restaurant by name if provided, otherwise by phone
    phone_number = ""
    if restaurant_name_input:
        restaurant = get_restaurant_by_name(restaurant_name_input)
        if restaurant:
            restaurant_id, restaurant_name = restaurant
        else:
            restaurant_id, restaurant_name = None, restaurant_name_input
    else:
        phone_number = sender.replace("whatsapp:", "") if sender else ""
        restaurant = get_restaurant_by_phone(phone_number)
        if restaurant:
            restaurant_id, restaurant_name = restaurant
        else:
            restaurant_id, restaurant_name = None, "Unknown"

    sender_info = restaurant_name_input if restaurant_name_input else (phone_number or sender or "Manual")
    print(f"📩 Message from {sender_info} -> {restaurant_name}: {body}")

    # 🤖 STEP 0: Pass through conversational agent to classify message
    agent_result = conversational_agent(body, restaurant_name)
    
    # If it's a natural message (not an order), handle differently
    if agent_result["type"] == "message":
        print(f"💬 Natural message detected from {restaurant_name}: {body}")
        
        # Save the message to restaurant_orders and conversations tables
        save_result = save_message(body, restaurant_id, restaurant_name)
        print(f"✅ Message saved: {save_result}")
        
        return {
            "status": "message_received",
            "message_type": "natural_conversation",
            "response": agent_result["response"],
            "original_message": body,
            "restaurant_name": restaurant_name,
            "display_alert": f"Message from {restaurant_name}: {body}"
        }
    
    # Otherwise, it's an order - save full message to conversations first, then process
    print(f"📦 Order detected from {restaurant_name}")
    
    # Save the full order message to conversations table (before processing into line items)
    save_to_conversations(body, restaurant_id, restaurant_name, direction="incoming")
    results = []

    # --- Step 1: AI-based unstructured parsing ---
    if "add" in body.lower() or "remove" in body.lower():
        try:
            parsed_items = ai_parse_order(body)
        except ValueError as e:
            # OpenAI not available, fall back to regular parsing
            print(f"⚠️  AI parsing unavailable: {e}. Falling back to regular parsing.")
            parsed_items = []
            # Continue with regular parsing flow below
        
        if parsed_items:
            for parsed in parsed_items:
                if parsed["action"] == "remove":
                    send_manager_alert(
                        restaurant=restaurant_name,
                        raw_message=body,
                        errors=["REMOVE request detected — manual handling required"]
                    )
                    results.append({"status": "red_alert", "item": parsed})
                else:
                    validated = validate_order({
                        "parsed": parsed,  # ✅ AI extracted fields
                        "extras": {
                            "raw_input": parsed.get("product", ""),  # ✅ raw guess from AI
                            "raw_matches": [parsed.get("product", "")]
                        }
                    })
                    validated["raw_message"] = body  # Store original message
                    saved = save_order(validated, restaurant_id, restaurant_name)
                    # Add parsed info to result
                    if saved.get("status") == "saved":
                        saved["parsed"] = validated.get("validated")
                        saved["original_input"] = parsed
                    results.append(saved)
        
        # If no AI parsing results, fall through to regular parsing
        if not parsed_items:
            normalize_body, line_mapping = normalize_order(body)
            incoming = input_text_tool(normalize_body, restaurant_name)

            for normalized_line in incoming["orders"]:
                # Get the original line before normalization
                # Normalized lines are already stripped by input_text_tool, so strip for lookup
                normalized_line_stripped = normalized_line.strip()
                original_line = line_mapping.get(normalized_line_stripped, normalized_line_stripped)
                
                parsed = parser_order(normalized_line_stripped)

                special = apply_special_cases(parsed["parsed"]["product"])
                if special:
                    parsed["parsed"]["product"] = special
                validated = validate_order(parsed)
                validated["raw_message"] = original_line  # Save original line, not normalized

                if validated.get("action") == "red_alert":
                    send_manager_alert(
                        restaurant=restaurant_name,
                        raw_message=original_line,  # Use original line
                        errors=validated.get("red_alerts", [])
                    )
                    # Still save the order even with red alert
                    saved = save_order(validated, restaurant_id, restaurant_name)
                    # Add parsed info to result
                    if saved.get("status") == "saved":
                        saved["parsed"] = validated.get("validated")
                        saved["original_parsed"] = parsed.get("parsed")
                    saved["raw_message"] = original_line  # Use original line
                    saved["red_alerts"] = validated.get("red_alerts", [])
                    results.append(saved)
                else:
                    saved = save_order(validated, restaurant_id, restaurant_name)
                    # Add parsed info to result
                    if saved.get("status") == "saved":
                        saved["parsed"] = validated.get("validated")
                        saved["original_parsed"] = parsed.get("parsed")
                    saved["raw_message"] = original_line  # Use original line
                    results.append(saved)
    else:
        normalize_body, line_mapping = normalize_order(body)
        incoming = input_text_tool(normalize_body, restaurant_name)

        for normalized_line in incoming["orders"]:
            # Get the original line before normalization
            # Normalized lines are already stripped by input_text_tool, so strip for lookup
            normalized_line_stripped = normalized_line.strip()
            original_line = line_mapping.get(normalized_line_stripped, normalized_line_stripped)
            
            parsed = parser_order(normalized_line_stripped)

            special = apply_special_cases(parsed["parsed"]["product"])
            if special:
                parsed["parsed"]["product"] = special
            validated = validate_order(parsed)
            validated["raw_message"] = original_line  # Save original line, not normalized

            if validated.get("action") == "red_alert":
                send_manager_alert(
                    restaurant=restaurant_name,
                    raw_message=original_line,  # Use original line
                    errors=validated.get("red_alerts", [])
                )
                # Still save the order even with red alert
                saved = save_order(validated, restaurant_id, restaurant_name)
                # Add parsed info to result
                if saved.get("status") == "saved":
                    saved["parsed"] = validated.get("validated")
                    saved["original_parsed"] = parsed.get("parsed")
                saved["raw_message"] = original_line  # Use original line
                saved["red_alerts"] = validated.get("red_alerts", [])
                results.append(saved)
            else:
                saved = save_order(validated, restaurant_id, restaurant_name)
                # Add parsed info to result
                if saved.get("status") == "saved":
                    saved["parsed"] = validated.get("validated")
                    saved["original_parsed"] = parsed.get("parsed")
                saved["raw_message"] = original_line  # Use original line
                results.append(saved)

    # --- Step 3: return summary with original message
    return {
        "status": "processed", 
        "orders": results,
        "original_message": body,
        "restaurant_name": restaurant_name
    }






