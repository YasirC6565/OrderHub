import os
import csv
from pathlib import Path
from datetime import datetime
from src.logger import log_correction

# Get the project root directory (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

def save_order(validated_output: dict, restaurant_id: int, restaurant_name: str, filepath = "orders.csv"):
    # Convert relative path to absolute path in project root
    if not os.path.isabs(filepath):
        filepath = PROJECT_ROOT / filepath
    filepath = str(filepath)
    # Allow saving even if product is missing (save with errors)
    if not validated_output.get("validated"):
        return {
            "status": "skipped",
            "errors": validated_output.get("errors", []),
            "raw_message": validated_output.get("raw_message", ""),
            "parsed": validated_output.get("validated", {})
        }

    # Step 2: check if file exists, open in append mode
    file_exists = os.path.isfile(filepath)
    with open(filepath, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            # Write header row matching database layout (Message at the end)
            writer.writerow([
                "restaurent_id",
                "restaurent_name",
                "quantity",
                "unit",
                "product",
                "corrections",
                "date",
                "original text",
                "need_attention",
                "Message"
            ])

        validated = validated_output["validated"]
        # Combine errors and red_alerts for the corrections column
        all_errors = validated_output.get("errors", []) + validated_output.get("red_alerts", [])
        errors = "; ".join(all_errors)
        # Format date in UK format: dd/mm/yyyy
        order_date = datetime.now().strftime("%d/%m/%Y")
        raw_message = validated_output.get("raw_message", "")
        need_attention = "YES" if validated_output.get("red_alerts") else "NO"
        # Mark as needing attention if there are red_alerts (stored in corrections column)
        if validated_output.get("red_alerts"):
            errors = errors if errors else "RED ALERT: " + "; ".join(validated_output.get("red_alerts", []))
        
        writer.writerow([
            restaurant_id,
            restaurant_name,
            validated.get("quantity"),
            validated.get("unit"),
            validated.get("product"),
            errors,  # corrections column (includes red alerts)
            order_date,  # date in UK format
            raw_message,  # original text
            need_attention,
            raw_message  # store the raw message in the Message column as well
        ])

        # ✅ Log corrections separately if errors or red_alerts exist
        if all_errors:
            log_correction(
                restaurant=restaurant_name,
                raw_message=validated_output.get("raw_message", ""),
                corrections=all_errors
            )

    # Step 4: return status with detailed info
    return {
        "status": "saved",
        "path": filepath,
        "parsed": validated,
        "raw_message": raw_message,
        "errors": validated_output.get("errors", [])
    }


def save_message(message: str, restaurant_id: int, restaurant_name: str, filepath = "orders.csv"):
    """
    Save a natural conversation message (not an order) to the CSV file.
    Only fills: restaurant_id, restaurant_name, date, and message columns.
    All order-related columns (quantity, unit, product) remain empty.
    Messages are flagged in corrections column for attention.
    """
    # Convert relative path to absolute path in project root
    if not os.path.isabs(filepath):
        filepath = PROJECT_ROOT / filepath
    filepath = str(filepath)
    
    # Check if file exists, open in append mode
    file_exists = os.path.isfile(filepath)
    with open(filepath, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            # Write header row matching database layout (Message at the end)
            writer.writerow([
                "restaurent_id",
                "restaurent_name",
                "quantity",
                "unit",
                "product",
                "corrections",
                "date",
                "original text",
                "need_attention",
                "Message"
            ])
        
        # Format date in UK format: dd/mm/yyyy
        order_date = datetime.now().strftime("%d/%m/%Y")
        
        # Write message row with empty order fields
        writer.writerow([
            restaurant_id,
            restaurant_name,
            "",  # quantity (empty)
            "",  # unit (empty)
            "",  # product (empty)
            "",  # corrections (empty for messages)
            order_date,  # date
            "",  # original text (empty for messages)
            "NEEDS ATTENTION - Customer Message",  # need_attention - messages need review
            message  # message column
        ])
    
    return {
        "status": "message_saved",
        "path": filepath,
        "message": message,
        "restaurant_name": restaurant_name
    }
