import csv
import os
from datetime import datetime

def log_correction(restaurant: str, raw_message: str, corrections: list[str], filepath="corrections.csv"):
    """
    Log corrections and flagged issues for human review.
    """
    file_exists = os.path.isfile(filepath)

    with open(filepath, mode="a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "restaurant", "original_order", "corrections"])

        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            restaurant,
            raw_message,
            "; ".join(corrections)
        ])

