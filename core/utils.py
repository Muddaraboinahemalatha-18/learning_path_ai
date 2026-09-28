import random
from django.core.mail import send_mail
from django.conf import settings

def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(email, otp):
    subject = "Your OTP Verification Code"
    message = f"""
    Dear User,

    Your OTP for account verification is: {otp}

    Do not share this OTP with anyone.

    Thank you.
    """
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
