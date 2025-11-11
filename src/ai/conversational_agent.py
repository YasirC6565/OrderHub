from src.ai.client import client
import json


def conversational_agent(message: str, restaurant_name: str):
    """
    Main conversational agent function for handling natural language interactions.
    Determines if message is an order or a natural conversation message.
    
    Args:
        message: User's input message
        restaurant_name: Name of the restaurant sending the message
    
    Returns:
        dict: {
            "type": "order" or "message",
            "response": reply to send back,
            "original_message": the original message,
            "restaurant_name": restaurant name
        }
    """
    if not client:
        # If OpenAI is not available, assume everything is an order
        return {
            "type": "order",
            "response": "Your message has been noted, and we will get back to you.",
            "original_message": message,
            "restaurant_name": restaurant_name
        }
    
    # Use OpenAI to classify the message
    prompt = f"""
You are a message classifier for an order management system.

Analyze this message and determine if it's:
1. An ORDER - contains product names, quantities, units (kg, bags, pieces, etc.)
2. A MESSAGE - a question, greeting, complaint, request for information, or general conversation

Message: "{message}"

Return ONLY valid JSON in this exact format:
{{
  "type": "order" or "message",
  "confidence": "high" or "medium" or "low"
}}

Examples:
- "5kg Onion, 3 bags Tomato" -> {{"type": "order", "confidence": "high"}}
- "Hello, do you have carrots available?" -> {{"type": "message", "confidence": "high"}}
- "Can I cancel my order?" -> {{"type": "message", "confidence": "high"}}
- "Thank you!" -> {{"type": "message", "confidence": "high"}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        classification = json.loads(response.choices[0].message.content)
        message_type = classification.get("type", "order")
        
        if message_type == "message":
            # It's a natural conversation message
            return {
                "type": "message",
                "response": "Your message has been noted, and we will get back to you.",
                "original_message": message,
                "restaurant_name": restaurant_name
            }
        else:
            # It's an order - process normally
            return {
                "type": "order",
                "response": None,  # Will be generated after processing
                "original_message": message,
                "restaurant_name": restaurant_name
            }
            
    except Exception as e:
        print(f"Error in conversational agent: {e}")
        # Default to treating as order if classification fails
        return {
            "type": "order",
            "response": None,
            "original_message": message,
            "restaurant_name": restaurant_name
        }


def get_welcome_message(restaurant_name: str, order_day: str = None) -> str:
    """
    Generate a welcome message for the restaurant.
    
    Args:
        restaurant_name: Name of the restaurant
        order_day: Optional day designation (e.g., "Monday", "today")
    
    Returns:
        str: Welcome message
    """
    if order_day:
        return f"Hello {restaurant_name}! Today is your designated order day. Please type your order below."
    else:
        return f"Hello {restaurant_name}! Welcome to OrderHub. Please type your order below."

