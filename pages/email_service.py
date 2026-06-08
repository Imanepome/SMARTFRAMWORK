import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

EMAIL_ADDRESS = "chalabiimane53@gmail.com"
EMAIL_PASSWORD = "clwn jxrf ljve fasv"


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp(email, otp):

    try:
        msg = MIMEMultipart()

        msg["From"] = EMAIL_ADDRESS
        msg["To"] = email
        msg["Subject"] = "Smart Grid Security OTP"

        body = f"""
Hello,

Your OTP code is:

{otp}

This code is valid for 5 minutes.

Regards,
FactoryNova Team
"""

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        server.login(
            EMAIL_ADDRESS,
            EMAIL_PASSWORD
        )

        server.sendmail(
            EMAIL_ADDRESS,
            email,
            msg.as_string()
        )

        server.quit()

        return True

    except Exception as e:
        print("Email Error:", e)
        return False