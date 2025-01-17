from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def send_sms(to, message):
    """
    Sends an SMS using Twilio.
    """
    # Fetch Twilio credentials from environment variables
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    phone_number = os.getenv("TWILIO_PHONE_NUMBER")

    if not account_sid or not auth_token or not phone_number:
        raise RuntimeError("Twilio credentials are missing in the .env file")

    # Initialize Twilio client
    client = Client(account_sid, auth_token)
    try:
        msg = client.messages.create(
            body=message,
            from_=phone_number,
            to=to
        )
        return msg.sid
    except Exception as e:
        raise RuntimeError(f"Error sending SMS: {str(e)}")
