
import os
from twilio.rest import Client

def send_manager_alert(restaurant: str, raw_message: str, errors: list[str]):
    """
    Send WhatsApp alert to the manager when red alert conditions are met.
    """
    client = Client(
        os.getenv("TWILIO_ACCOUNT_SID"),
        os.getenv("TWILIO_AUTH_TOKEN")
    )

    body = (
        "🚨 ORDER ALERT 🚨\n\n"
        f"Restaurant: {restaurant}\n"
        f"Original message: {raw_message}\n"
        f"Issues: {', '.join(errors)}"
    )

    client.messages.create(
        from_=os.getenv("TWILIO_WHATSAPP_NUMBER"),
        to=os.getenv("MANAGER_WHATSAPP_NUMBER"),
        body=body
    )
