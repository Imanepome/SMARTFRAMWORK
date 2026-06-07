import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from python_http_client.exceptions import HTTPError

SENDGRID_API_KEY = "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"
SENDER_EMAIL = "chalabiimane53@gmail.com"

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(email, otp):
    print("Starting send_otp...")
    print("Recipient:", email)

    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=email,
        subject="Smart Grid Security OTP",
        html_content=f"<h1>{otp}</h1>"
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        print("SendGrid client created")

        response = sg.send(message)
    except HTTPError as e:
        print("Status:", e.status_code)
        print("Body:", e.body)

        

    except Exception as e:
        print("ERROR:", e)