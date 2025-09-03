import os
import csv
from src.logger import log_correction



def save_order(validated_output: dict, restaurant_id: int, restaurant_name: str, filepath = "orders.csv"):
    if (not validated_output.get("validated")
            or not validated_output["validated"].get("product")):
        return {
            "status": "skipped",
            "errors": validated_output.get("errors")
        }

    # Step 2: check if file exists, open in append mode
    file_exists = os.path.isfile(filepath)
    with open(filepath, mode="a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            # Write header row once
            writer.writerow(["restaurant_id","restaurant_name","quantity", "unit", "product","errors"])

        validated = validated_output["validated"]
        errors = "; ".join(validated_output.get("errors", []))
        writer.writerow([
            restaurant_id,
            restaurant_name,
            validated.get("quantity"),
            validated.get("unit"),
            validated.get("product"),
            errors
        ])

        # ✅ Log corrections separately if errors exist
        if validated_output.get("errors"):
            log_correction(
                restaurant=restaurant_name,
                raw_message=validated_output.get("raw_message", ""),
                corrections=validated_output.get("errors")
            )

    # Step 4: return status
    return {
        "status": "saved",
        "path": filepath
    }

