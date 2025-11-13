from src.ai.matcher import (suggest_product_ai, suggest_product_fuzzy,
                            phonetic_match)
from src.utils.special_cases import apply_special_cases, SPECIAL_CASES

from src.db import get_products
from src.parser import get_primary_units

def validate_order(parsed_output: dict) -> dict:
    parsed = parsed_output.get("parsed", {})
    errors = []
    red_alerts = []

    #debug prints
    raw_word = parsed_output.get("extras", {}).get("raw_input", "")
    print("DEBUG RAW WORD:", repr(raw_word))

    product_names = [name for name, _ in get_products()]
    print("DEBUG PRODUCT NAMES:", product_names)
    
    # Debug parsed values
    print(f"DEBUG PARSED: quantity={parsed.get('quantity')}, unit={parsed.get('unit')}, product={parsed.get('product')}")

    #quantity
    if parsed.get("quantity") is None:
        red_alerts.append("Missing quantity")

    #unit - if missing, try to use product's primary unit
    if parsed.get("unit") is None:
        # Try to get primary unit from product
        product = parsed.get("product")
        if product:
            primary_units = get_primary_units()
            product_lower = product.lower().strip()
            primary_unit = primary_units.get(product_lower)
            
            # If exact match fails, try case-insensitive partial match
            if not primary_unit:
                for prod_name, prod_unit in primary_units.items():
                    if product_lower in prod_name.lower() or prod_name.lower() in product_lower:
                        primary_unit = prod_unit
                        print(f"🔍 Matched product '{product}' to '{prod_name}' for primary unit lookup")
                        break
            
            if primary_unit:
                # Map primary unit to standard unit name
                unit_map = {
                    "bag": "Bag",
                    "pieces": "Pieces",
                    "box": "Box",
                    "kilogram": "Kilogram",
                    "kg": "Kilogram",
                    "bunch": "Pieces",
                    "tray": "Pieces",
                    "bucket": "Bucket"
                }
                parsed["unit"] = unit_map.get(primary_unit.lower(), primary_unit.capitalize())
                errors.append(f"Unit auto-assigned: {parsed['unit']} (primary unit for {product})")
                print(f"✅ Auto-assigned unit '{parsed['unit']}' for product '{product}'")
            else:
                print(f"⚠️  No primary unit found for product '{product}' (checked: {product_lower})")
                red_alerts.append("Missing unit")
        else:
            red_alerts.append("Missing unit")

    #product
    # if parsed.get("product") is None:
    raw_word = parsed_output.get("extras", {}).get("raw_input", "").strip()

    if parsed.get("product") and parsed["product"] in SPECIAL_CASES.values():
        pass  # do nothing, keep it locked in

    elif not parsed.get("product") or parsed["product"] not in product_names:
            suggestion = apply_special_cases(raw_word)

            if not suggestion:
                suggestion = suggest_product_ai(raw_word, product_names)

            if not suggestion:
                suggestion = phonetic_match(raw_word, product_names)

            if not suggestion:
                suggestion = suggest_product_fuzzy(raw_word, product_names)

            if suggestion:
                parsed["product"] = suggestion
                if suggestion.lower() != raw_word.lower():
                    errors.append(f"Product corrected from '{raw_word}' to '{suggestion}'")
            else:
                red_alerts.append(f"Unknown product: {raw_word}")

    extras = parsed_output.get("extras", {}).get("raw_matches", [])
    if len(extras) > 1:
        red_alerts.append(f"Multiple products detected: {', '.join(extras)}")

    if not parsed.get("quantity") and not parsed.get("unit") and not parsed.get("product"):
        red_alerts.append("Message does not contain a valid order")

    if errors:
        action = "send_to_human"
    else:
        action = "continue"

    if red_alerts:
        return {
            "validated": parsed,  # ✅ still include parsed data even with errors
            "errors": errors,  # low-level corrections (if any before fail)
            "red_alerts": red_alerts,  # 🚨 reasons
            "action": "red_alert"
        }
    else:
        return{
            "validated": parsed,
            "errors": errors,
            "action": action
        }




