from celery import shared_task
from django.core.mail import send_mail

from root.settings import EMAIL_HOST_USER


@shared_task()
def send_email_task(to_email, code):
    subject = "Verify"
    message = f"Your verification code: {code}"
    from_email = EMAIL_HOST_USER
    recipient_list = [to_email]
    send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
    return "Send"
