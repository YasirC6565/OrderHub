
def input_text_tool(input_text: str, restaurant_name: str):
    raw_orders = input_text.strip().splitlines()
    return {
        "restaurant": restaurant_name,
        "orders": raw_orders
    }

