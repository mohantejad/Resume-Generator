import os
import resend
from dotenv import load_dotenv

load_dotenv()


resend.api_key =os.getenv('RESEND_API_KEY')

async def send_activation_email(email: str, token: str):
    activation_link = f"{os.getenv('FRONTEND_URL')}/activate?token={token}"
    email_body = f"Click the link to activate your account: {activation_link}"

    try:
        response = resend.Emails.send(
            {
                "from": os.getenv('RESEND_SENDER_EMAIL'), 
                "to": [email],
                "subject": "Activate Your Account",
                "text": email_body,
            }
        )
        print("Activation email sent successfully!", response)
        return response
    except Exception as e:
        print(f"Error sending email: {e}")
        return None
