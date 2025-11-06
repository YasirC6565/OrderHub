import csv
import os
from pathlib import Path
from datetime import datetime

# Get the project root directory (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

def log_correction(restaurant: str, raw_message: str, corrections: list[str], filepath="corrections.csv"):
    """
    Log corrections and flagged issues for human review.
    """
    # Convert relative path to absolute path in project root
    if not os.path.isabs(filepath):
        filepath = PROJECT_ROOT / filepath
    filepath = str(filepath)
    
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

