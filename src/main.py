from src.parser import parser_order
from src.utils.special_cases import apply_special_cases
from src.validator import validate_order
from src.saver import save_order
from src.input_tool import input_text_tool
from src.db import get_products, get_restaurant_by_name, get_restaurant_by_phone
from src.alerts import send_manager_alert
from src.ai.order_parser import ai_parse_order, normalize_order
from fastapi import FastAPI, Request
from dotenv import load_dotenv
load_dotenv()


app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    sender = form.get("From")
    body = form.get("Body")

    phone_number = sender.replace("whatsapp:", "")

    # 🔑 Lookup restaurant by phone
    restaurant = get_restaurant_by_phone(phone_number)
    if restaurant:
        restaurant_id, restaurant_name = restaurant
    else:
        restaurant_id, restaurant_name = None, "Unknown"

    print(f"📩 WhatsApp from {phone_number} -> {restaurant_name}: {body}")

    results = []

    # --- Step 1: AI-based unstructured parsing ---
    if "add" in body.lower() or "remove" in body.lower():
        parsed_items = ai_parse_order(body)

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
                saved = save_order(validated, restaurant_id, restaurant_name)
                results.append(saved)
    else:
        normalize_body = normalize_order(body)
        incoming = input_text_tool(normalize_body, restaurant_name)

        for line in incoming["orders"]:
            parsed = parser_order(line)

            special = apply_special_cases(parsed["parsed"]["product"])
            if special:
                parsed["parsed"]["product"] = special
            validated = validate_order(parsed)
            validated["raw_message"] = line

            if validated.get("action") == "red_alert":
                send_manager_alert(
                    restaurant=restaurant_name,
                    raw_message=line,
                    errors=validated.get("red_alerts", [])
                )
            saved = save_order(validated, restaurant_id, restaurant_name)
            results.append(saved)

    # --- Step 3: return summary
    return {"status": "processed", "orders": results}






