import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = "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"
SENDER_EMAIL = "chalabiimane53@gmail.com"

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(email, otp):
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=email,
        subject="Smart Grid Security OTP",
        html_content=f"""
        <h2>⚡ Smart Grid Secure System</h2>
        <p>Your OTP code is:</p>
        <h1>{otp}</h1>
        <p>This code will expire in 5 minutes.</p>
        """
        )

    sg = SendGridAPIClient(SENDGRID_API_KEY)
    sg.send(message)
    