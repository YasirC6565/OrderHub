from src.parser import parser_order
from src.utils.special_cases import apply_special_cases
from src.validator import validate_order
from src.saver import save_order
from src.input_tool import input_text_tool
from src.db import get_products, get_restaurant_by_name, get_restaurant_by_phone
from src.alerts import send_manager_alert
from src.ai.order_parser import ai_parse_order, normalize_order
from src.history import get_order_history, get_today_orders
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from datetime import datetime
import os
load_dotenv()


app = FastAPI()

# Enable CORS for frontend connection
# Allow localhost for development and Vercel domains for production
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://order-hub-nine.vercel.app",  # Your Vercel domain
]

# Add Vercel domain from environment variable if set
vercel_url = os.getenv("VERCEL_URL")
if vercel_url:
    # Handle both with and without https
    if not vercel_url.startswith("http"):
        allowed_origins.append(f"https://{vercel_url}")
        allowed_origins.append(f"http://{vercel_url}")
    else:
        allowed_origins.append(vercel_url)

# Also allow any vercel.app domain (for preview deployments)
# Use regex pattern for wildcard matching
allowed_origin_regex = r"https://.*\.vercel\.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allowed_origin_regex,
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
        orders = get_order_history()
        return {"orders": orders}
    except Exception as e:
        print(f"Error loading history: {e}")
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
    print(f"📩 Order from {sender_info} -> {restaurant_name}: {body}")

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






