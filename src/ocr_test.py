from openai import OpenAI
import base64
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def read_order_image(image_path: str):
    # Load and encode image as base64

    prompt = f"""

    """

    with open(image_path, "rb") as f:
        b64_image = base64.b64encode(f.read()).decode("utf-8")

    # Send to ChatGPT-5 (GPT-4o model for vision)
    response = client.chat.completions.create(
        model="gpt-5-chat-latest",  # vision-enabled model
        messages=[
            {"role": "system",
             "content": "You are an assistant that reads restaurant order sheets. "
                    "Follow these rules:\n"
                    "- Units mapping: 'bx' = 'box', 'pc' or 'p' = 'piece', 'kg' = 'kilogram', 'bg' = 'bag'.\n"
                    "- If unit is missing, assume the product’s primary unit (use 'piece' as fallback).\n"
                    "- Ignore headers, phone numbers, or non-product text.\n"
                    "- Output should be a natural list, e.g. '3 boxes of Coriander, 2 pieces of Lemon'."
                    "- if no quantity, just list the product name"},
            {"role": "user", "content": [
                {"type": "text", "text": "Can you read this image and tell me what the restaurant ordered?"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image}"}}
            ]}
        ]
    )

    # Normal chat reply (not JSON enforced)
    return response.choices[0].message.content


# Example usage
print(read_order_image(r"C:\Users\chowd\Documents\AI\OrderHub\templates\test_template.png"))



