from src.parser import parser_order
from src.utils.special_cases import apply_special_cases
from src.validator import validate_order
from src.saver import save_order, save_message, save_to_conversations, save_checked_order
from src.input_tool import input_text_tool
from src.db import get_products, get_restaurant_by_name, get_restaurant_by_phone
from src.alerts import send_manager_alert
from src.ai.order_parser import ai_parse_order, normalize_order
from src.ai.conversational_agent import conversational_agent, get_welcome_message
from src.history import get_order_history, get_today_orders, get_messages
from src.conversations import get_all_conversations
from fastapi import FastAPI, Request, Query
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from datetime import datetime
import os
load_dotenv()


app = FastAPI()

# Enable CORS for frontend connection
# Allow ONLY specific origins (no wildcard for security)
# Get frontend URL from environment variable or use defaults
frontend_url = os.getenv("FRONTEND_URL", "https://order-hub-nine.vercel.app")

allowed_origins = [
    "https://order-hub-nine.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Add frontend URL from env if it's not already in the list
if frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)

print(f"🌐 CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
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

class ReplyRequest(BaseModel):
    message_id: int
    reply_text: str
    restaurant_id: Optional[int] = None
    restaurant_name: str

@app.options("/messages/reply")
async def reply_options():
    """Handle CORS preflight requests"""
    return {"status": "ok"}

@app.post("/messages/reply")
def reply_to_message(reply_request: ReplyRequest):
    """Reply to a message - saves reply to conversations table and updates need_attention flag"""
    try:
        from src.saver import get_database_engine, save_to_conversations
        from sqlalchemy import text
        
        # Debug logging
        print(f"📩 Received reply request:")
        print(f"   Message ID: {reply_request.message_id}")
        print(f"   Reply Text: {reply_request.reply_text}")
        print(f"   Restaurant: {reply_request.restaurant_name}")
        print(f"   Restaurant ID: {reply_request.restaurant_id}")
        
        engine = get_database_engine()
        
        # First, get the original message from restaurant_orders
        get_original_query = text("""
            SELECT message, restaurant_name, restaurant_id, date
            FROM restaurant_orders
            WHERE id = :message_id
        """)
        
        with engine.connect() as conn:
            result = conn.execute(get_original_query, {"message_id": reply_request.message_id})
            original_row = result.fetchone()
            
            if not original_row:
                return {
                    "status": "error",
                    "message": f"Message with id {reply_request.message_id} not found"
                }
            
            original_message = original_row[0] or ""
            original_restaurant_name = original_row[1]
            original_restaurant_id = original_row[2]
        
        # Find or create the conversations entry for the original message
        # First, try to find an existing conversations entry for this message
        find_conversation_query = text("""
            SELECT id 
            FROM conversations 
            WHERE restaurant_name = :restaurant_name 
            AND message = :message
            AND direction = 'incoming'
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        parent_conversation_id = None
        with engine.connect() as conn:
            result = conn.execute(find_conversation_query, {
                "restaurant_name": original_restaurant_name,
                "message": original_message
            })
            row = result.fetchone()
            if row:
                parent_conversation_id = row[0]
                print(f"✅ Found existing conversations entry with ID: {parent_conversation_id}")
        
        # If no conversations entry exists for the original message, create one
        if parent_conversation_id is None:
            print(f"📝 Creating conversations entry for original message...")
            try:
                save_to_conversations(
                    message=original_message,
                    restaurant_id=original_restaurant_id if original_restaurant_id else None,
                    restaurant_name=original_restaurant_name,
                    direction="incoming",
                    parent_message_id=None
                )
                # Now find the ID of the conversation we just created
                with engine.connect() as conn:
                    result = conn.execute(find_conversation_query, {
                        "restaurant_name": original_restaurant_name,
                        "message": original_message
                    })
                    row = result.fetchone()
                    if row:
                        parent_conversation_id = row[0]
                        print(f"✅ Created and found conversations entry with ID: {parent_conversation_id}")
            except Exception as create_error:
                print(f"⚠️  Warning: Could not create conversations entry for original message: {create_error}")
                # Continue anyway, we'll save the reply without a parent
        
        # Save reply to conversations table with parent_message_id pointing to conversations table
        try:
            save_to_conversations(
                message=reply_request.reply_text,
                restaurant_id=reply_request.restaurant_id if reply_request.restaurant_id else None,
                restaurant_name=reply_request.restaurant_name,
                direction="outgoing",
                parent_message_id=parent_conversation_id  # Use conversations.id as parent reference
            )
            print(f"✅ Successfully saved reply to conversations table with parent_message_id={parent_conversation_id}")
        except Exception as save_error:
            print(f"❌ Failed to save to conversations table: {save_error}")
            import traceback
            traceback.print_exc()
            # Still continue to update need_attention, but return an error status
            return {
                "status": "error",
                "message": f"Failed to save reply to conversations table: {str(save_error)}"
            }
        
        # Verify the message was saved by querying it back
        verify_query = text("""
            SELECT message, created_at 
            FROM conversations 
            WHERE restaurant_name = :restaurant_name 
            AND direction = 'outgoing' 
            AND parent_message_id = :parent_message_id
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        
        saved_message = None
        with engine.connect() as conn:
            verify_result = conn.execute(verify_query, {
                "restaurant_name": reply_request.restaurant_name,
                "parent_message_id": parent_conversation_id
            })
            saved_row = verify_result.fetchone()
            
            if saved_row:
                saved_message = saved_row[0]
                print(f"✅ Verified saved message: {saved_message[:100]}{'...' if len(saved_message) > 100 else ''}")
                if saved_message != reply_request.reply_text:
                    print(f"⚠️  WARNING: Saved message doesn't match sent message!")
                    print(f"   Sent: {reply_request.reply_text[:100]}")
                    print(f"   Saved: {saved_message[:100]}")
            else:
                print(f"⚠️  WARNING: Could not verify saved message - query returned no results")
        
        # Update need_attention flag to False in restaurant_orders table
        query = text("""
            UPDATE restaurant_orders
            SET need_attention = FALSE
            WHERE id = :message_id
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {"message_id": reply_request.message_id})
            conn.commit()
        
        if result.rowcount > 0:
            return {
                "status": "success",
                "message": "Reply sent successfully",
                "message_id": reply_request.message_id,
                "saved_message": saved_message
            }
        else:
            return {
                "status": "error",
                "message": f"Message with id {reply_request.message_id} not found"
            }
    
    except Exception as e:
        print(f"Error replying to message: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

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

@app.put("/order/{order_id}")
def update_order_item(
    order_id: int,
    product: str = Query(None),
    quantity: str = Query(None),
    unit: str = Query(None)
):
    """Update a single order item by ID"""
    try:
        from src.saver import get_database_engine
        from sqlalchemy import text
        
        engine = get_database_engine()
        
        # Build update query dynamically based on provided parameters
        updates = []
        params = {"order_id": order_id}
        
        # Handle product update (empty string means clear the field)
        if product is not None:
            updates.append("product = :product")
            params["product"] = product.strip() if product.strip() else None
        
        # Handle quantity update (empty string means clear the field)
        if quantity is not None:
            updates.append("quantity = :quantity")
            params["quantity"] = quantity.strip() if quantity.strip() else None
        
        # Handle unit update (empty string means clear the field)
        if unit is not None:
            updates.append("unit = :unit")
            params["unit"] = unit.strip() if unit.strip() else None
        
        if not updates:
            return {"status": "error", "message": "No fields provided for update"}
        
        # Build and execute update query
        query = text(f"UPDATE restaurant_orders SET {', '.join(updates)} WHERE id = :order_id")
        
        with engine.connect() as conn:
            result = conn.execute(query, params)
            conn.commit()
            
        if result.rowcount > 0:
            return {"status": "updated", "message": f"Order item {order_id} updated successfully"}
        else:
            return {"status": "not_found", "message": f"Order item {order_id} not found"}
    except Exception as e:
        print(f"Error updating order item: {e}")
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

@app.post("/orders/check")
def mark_order_checked(restaurant_name: str = Query(...), order_date: str = Query(...)):
    """Mark an order as checked by updating checked_at timestamp"""
    try:
        from src.saver import get_database_engine
        from sqlalchemy import text
        from datetime import datetime
        
        engine = get_database_engine()
        
        # Parse date from DD/MM/YYYY format
        try:
            date_obj = datetime.strptime(order_date, "%d/%m/%Y").date()
        except:
            return {"status": "error", "message": "Invalid date format. Use DD/MM/YYYY"}
        
        # Update checked_at timestamp (or insert if doesn't exist)
        query = text("""
            INSERT INTO checked_orders (restaurant_name, order_date, checked_at, amount_of_products)
            VALUES (:restaurant_name, :order_date, :checked_at, 
                    COALESCE((SELECT COUNT(*) FROM restaurant_orders 
                             WHERE restaurant_name = :restaurant_name 
                             AND DATE(date) = :order_date 
                             AND product IS NOT NULL AND product != ''), 0))
            ON CONFLICT (restaurant_name, order_date) 
            DO UPDATE SET checked_at = :checked_at
        """)
        
        with engine.begin() as conn:
            result = conn.execute(query, {
                "restaurant_name": restaurant_name,
                "order_date": date_obj,
                "checked_at": datetime.now()
            })
        
        return {"status": "checked", "message": f"Order marked as checked"}
    
    except Exception as e:
        print(f"Error marking order as checked: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.post("/orders/uncheck")
def mark_order_unchecked(restaurant_name: str = Query(...), order_date: str = Query(...)):
    """Mark an order as unchecked by setting checked_at to null"""
    try:
        from src.saver import get_database_engine
        from sqlalchemy import text
        from datetime import datetime
        
        engine = get_database_engine()
        
        # Parse date from DD/MM/YYYY format
        try:
            date_obj = datetime.strptime(order_date, "%d/%m/%Y").date()
        except:
            return {"status": "error", "message": "Invalid date format. Use DD/MM/YYYY"}
        
        # Set checked_at to null
        query = text("""
            UPDATE checked_orders
            SET checked_at = NULL
            WHERE restaurant_name = :restaurant_name
                AND order_date = :order_date
        """)
        
        with engine.begin() as conn:
            result = conn.execute(query, {
                "restaurant_name": restaurant_name,
                "order_date": date_obj
            })
        
        return {"status": "unchecked", "message": f"Order marked as unchecked"}
    
    except Exception as e:
        print(f"Error marking order as unchecked: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.get("/orders/checked")
def get_checked_orders():
    """Get all checked orders (orders with checked_at not null)"""
    try:
        from src.saver import get_database_engine
        from sqlalchemy import text
        
        engine = get_database_engine()
        
        query = text("""
            SELECT restaurant_name, order_date
            FROM checked_orders
            WHERE checked_at IS NOT NULL
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query)
            rows = result.fetchall()
        
        # Format as "restaurant_name|DD/MM/YYYY" to match frontend format
        checked_orders = []
        for restaurant_name, order_date in rows:
            if order_date:
                date_str = order_date.strftime("%d/%m/%Y") if hasattr(order_date, 'strftime') else str(order_date)
                checked_orders.append(f"{restaurant_name}|{date_str}")
        
        return {"checked_orders": checked_orders}
    
    except Exception as e:
        print(f"Error getting checked orders: {e}")
        import traceback
        traceback.print_exc()
        return {"checked_orders": [], "error": str(e)}

@app.get("/whatsapp")
def whatsapp_health():
    return {"status": "ok"}

@app.options("/whatsapp")
async def whatsapp_options():
    """Handle CORS preflight requests"""
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
    saved_count = 0  # Track how many orders we successfully save

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
                        saved_count += 1
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
                        saved_count += 1
                    saved["raw_message"] = original_line  # Use original line
                    saved["red_alerts"] = validated.get("red_alerts", [])
                    results.append(saved)
                else:
                    saved = save_order(validated, restaurant_id, restaurant_name)
                    # Add parsed info to result
                    if saved.get("status") == "saved":
                        saved["parsed"] = validated.get("validated")
                        saved["original_parsed"] = parsed.get("parsed")
                        saved_count += 1
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
                    saved_count += 1
                saved["raw_message"] = original_line  # Use original line
                saved["red_alerts"] = validated.get("red_alerts", [])
                results.append(saved)
            else:
                saved = save_order(validated, restaurant_id, restaurant_name)
                # Add parsed info to result
                if saved.get("status") == "saved":
                    saved["parsed"] = validated.get("validated")
                    saved["original_parsed"] = parsed.get("parsed")
                    saved_count += 1
                saved["raw_message"] = original_line  # Use original line
                results.append(saved)

    # --- Step 3: Save grouped order to checked_orders table
    # Save to checked_orders if we saved any orders
    if saved_count > 0:
        save_checked_order(restaurant_name, amount_of_products=saved_count)

    # --- Step 4: return summary with original message
    return {
        "status": "processed", 
        "orders": results,
        "original_message": body,
        "restaurant_name": restaurant_name
    }






