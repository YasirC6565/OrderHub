
def input_text_tool(input_text: str, restaurant_name: str):
    # Strip each line to match the normalized lines in the mapping
    raw_orders = [line.strip() for line in input_text.strip().splitlines() if line.strip()]
    return {
        "restaurant": restaurant_name,
        "orders": raw_orders
    }

