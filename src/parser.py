import re

from src.db import get_products
from src.utils.special_cases import apply_special_cases

UNIT_MAP = {
        "p": "Pieces",
        "pc":"Pieces",
        "bg": "Bag",
        "kg": "Kilogram",
        "bx": "Box",
        "box": "Box",
        "kilo": "Kilogram",
        "k": "Kilogram",
        "kilogram": "Kilogram",
        "bag": "Bag",
        "piece": "Pieces",
        "tray": "Pieces",
        "bunch": "Pieces"
    }

PRODUCT_CATALOG = ["onion", "cola", "rice"]

def extract_product(input_order: str) -> str | None:
    text = re.sub(r"[^a-z0-9\s]", " ", input_order.lower())
    matches = []

    products = sorted(get_products(), key=lambda x: len(x[0]), reverse=True)

    for name, units in products:
        pattern = r"\b" + re.escape(name.lower()) + r"\b"
        if re.search(pattern, text):
            return [name]
    return matches


def parser_order(input_order):

    # quantity
    qmatch = re.search(r"\d+(\.\d+)?", input_order)
    quantity = float(qmatch.group()) if qmatch else None

    #product - extract FIRST to avoid matching product name as unit
    matches = extract_product(input_order)
    product = matches[0] if matches else None

    #unit - extract AFTER product to avoid capturing product name
    # Match valid unit abbreviations (1-4 chars) that come after the number
    unit = None
    
    # Try short unit abbreviations first (bg, kg, bx, p, pc, k)
    short_unit_match = re.search(r"\d+\s*([a-zA-Z]{1,4})\s", input_order)
    if short_unit_match:
        raw_unit = short_unit_match.group(1).lower()
        if raw_unit in UNIT_MAP:
            unit = UNIT_MAP.get(raw_unit, None)
    
    # If no short unit found, try full unit words
    if not unit:
        unit_pattern = r"\b(bag|box|kilogram|piece|pieces|bunch|tray|bucket)\b"
        unit_match = re.search(unit_pattern, input_order.lower())
        if unit_match:
            raw_unit = unit_match.group(1).lower()
            unit = UNIT_MAP.get(raw_unit, None)

    if product:
        special = apply_special_cases(input_order)
        if special:
            product = special

    # raw_input = input_order.strip().split()[-1]
    # raw_input = matches[0] if matches else input_order.strip()
    raw_input = input_order.strip()

    return {
            "parsed": {
                "quantity": quantity,
                "unit": unit,
                "product": product,

            },
            "extras": {
                "raw_matches": matches,
                "raw_input": raw_input

            }
        }


def get_primary_units():
    product_units = {}
    for name, units in get_products():  # e.g. ("Cabbage White", ["bag", "pieces"])
        if units:
            primary = units[0]  # take the first unit as default
            product_units[name.lower()] = primary
    return product_units

