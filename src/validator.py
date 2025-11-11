from src.ai.matcher import (suggest_product_ai, suggest_product_fuzzy,
                            phonetic_match)
from src.utils.special_cases import apply_special_cases, SPECIAL_CASES

from src.db import get_products

def validate_order(parsed_output: dict) -> dict:
    parsed = parsed_output.get("parsed", {})
    errors = []
    red_alerts = []

    #debug prints
    raw_word = parsed_output.get("extras", {}).get("raw_input", "")
    print("DEBUG RAW WORD:", repr(raw_word))

    product_names = [name for name, _ in get_products()]
    print("DEBUG PRODUCT NAMES:", product_names)

    #quantity
    if parsed.get("quantity") is None:
        red_alerts.append("Missing quantity")

    #unit
    if parsed.get("unit") is None:
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




