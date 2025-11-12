from openai import OpenAI
import os
import json
from src.parser import get_primary_units, get_products
import re

# Initialize client only if API key is available
_api_key = os.getenv("OPENAI_API_KEY")
if _api_key:
    client = OpenAI(api_key=_api_key)
else:
    client = None
    print("⚠️  Warning: OPENAI_API_KEY not set in order_parser. AI parsing will be disabled.")

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

def ai_parse_order(message: str) -> dict:
    """
    Uses OpenAI to parse an unstructured order raw_message into structured fields.
    """
    if not client:
        raise ValueError("OpenAI client not initialized. Please set OPENAI_API_KEY environment variable.")
    
    prompt = f"""
    You are an order parsing assistant. 
Extract all items from the raw_message. Each item must include: action (add/remove), quantity, unit, product.
If action is not specified, assume "add".

Message: "{message}"

Return ONLY valid JSON, in this exact format:
{{
  "items": [
    {{"action": "...", "quantity": <int>, "unit": "...", "product": "..."}},
    {{"action": "...", "quantity": <int>, "unit": "...", "product": "..."}}
  ]
}}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            timeout=15.0  # 15 second timeout for full order parsing
        )
    except Exception as e:
        raise ValueError(f"AI parsing failed: {e}")

    parsed = json.loads(response.choices[0].message.content)
    return parsed.get("items", [])

def get_unit_abbreviations():
    reverse_map = {}
    for abbr, fullname in UNIT_MAP.items():
        # prefer lowercase keys, but keep consistent with parser
        reverse_map[fullname.lower()] = abbr
    # Make a string for the prompt
    return "\n".join([f"{fullname} → {abbr}" for fullname, abbr in reverse_map.items()])

def is_order_line(line: str) -> bool:
    """Check if a line looks like an order (quantity or product match)."""
    if re.search(r"\d+", line):  # has a number
        return True
    products = [name.lower() for name, _ in get_products()]
    text = line.lower()
    return any(p in text for p in products)

def normalize_order(raw_message: str) -> tuple[str, dict[str, str]]:
    """
    Normalizes messy order input into clean, parser-friendly lines.
    Example: "ONION-3" -> "3 bg Onion"
    Returns: (normalized_text, mapping of normalized_line -> original_line)
    """
    if not client:
        # If OpenAI is not available, return original message with identity mapping
        lines = [line.strip() for line in raw_message.splitlines() if line.strip()]
        line_mapping = {line: line for line in lines}
        return raw_message, line_mapping
    
    original_lines = [line.strip() for line in raw_message.splitlines() if line.strip()]
    normalized_lines = []
    line_mapping = {}  # Maps normalized line -> original line
    
    # Quick check: if all lines already look like clean orders, skip normalization
    # This avoids unnecessary API calls for already-clean orders
    # A line is "clean" if it has a number and either:
    # 1. Has a unit abbreviation, OR
    # 2. Has a product name that matches our product list
    all_lines_clean = True
    products = [name.lower() for name, _ in get_products()]
    for line in original_lines:
        if is_order_line(line):
            has_number = bool(re.search(r'\d+', line))
            has_unit_abbr = bool(re.search(r'\d+\s*(bg|kg|bx|box|p|pc|k|kilo|bag|piece|tray|bunch)', line, re.IGNORECASE))
            # Check if line contains a known product name
            line_lower = line.lower()
            has_product = any(p in line_lower for p in products)
            
            # If it has a number and (unit OR product), it's probably clean enough
            if not (has_number and (has_unit_abbr or has_product)):
                all_lines_clean = False
                break
    
    # If all lines are already clean, return as-is (skip expensive normalization)
    if all_lines_clean:
        print("✅ Order already in clean format, skipping normalization")
        for line in original_lines:
            normalized_lines.append(line)
            line_mapping[line] = line
        return raw_message, line_mapping
    
    # Otherwise, normalize each line that needs it
    primary_units = get_primary_units()
    unit_map_str = "\n".join([f"{prod} → {unit}" for prod, unit in primary_units.items()])
    unit_abbr_str = get_unit_abbreviations()

    for original_line in original_lines:
        if not is_order_line(original_line):
            normalized_lines.append(original_line)
            line_mapping[original_line] = original_line  # Non-order lines stay the same
            continue

        prompt = f"""
                You are an order text normalizer.
                Convert this order line into a clean format:
                - Always: <quantity><PRIMARY unit abbreviation> <Product>
                  (e.g., 3bg Onion, 1bx Tomato)
                - If client provides a valid unit (from this list), keep it:
                {unit_abbr_str}
                - If no unit is given, use the product's PRIMARY unit:
                {unit_map_str}
                - If no quantity is present, return the input exactly as-is.
                - Do not invent or assume a quantity.
                - Convert fractions like ½ to decimals (0.5).
                - Capitalize product names properly.
                - Output only the normalized line, no commentary.
                
                e.g:
                - "CARROT-5kg" -> "5kg Carrot" 

                Input: {original_line}
                Output:
                """

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                timeout=10.0  # 10 second timeout per line
            )
        except Exception as e:
            # If normalization fails, use original line
            print(f"⚠️  Normalization failed for line '{original_line}': {e}")
            normalized_lines.append(original_line)
            line_mapping[original_line] = original_line
            continue

        normalized = response.choices[0].message.content.strip()
        normalized = normalized.replace("```", "").replace("'''", "").strip()

        if normalized:  # only add if non-empty
            normalized_lines.append(normalized)
            line_mapping[normalized] = original_line  # Map normalized -> original

    # Join back into one clean string
    normalized_text = "\n".join(normalized_lines)
    return normalized_text, line_mapping
