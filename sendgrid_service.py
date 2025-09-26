import os
import sys
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

def send_email(
    to_email: str,
    from_email: str,
    subject: str,
    text_content: str | None = None,
    html_content: str | None = None
) -> bool:
    """
    Send an email using SendGrid API
    """
    sendgrid_key = os.environ.get('SENDGRID_API_KEY')
    if not sendgrid_key:
        print('SENDGRID_API_KEY environment variable must be set')
        return False
    
    sg = SendGridAPIClient(sendgrid_key)

    message = Mail(
        from_email=Email(from_email),
        to_emails=To(to_email),
        subject=subject
    )

    if html_content:
        message.content = Content("text/html", html_content)
    elif text_content:
        message.content = Content("text/plain", text_content)
    else:
        message.content = Content("text/plain", "No content provided")

    try:
        response = sg.send(message)
        print(f"Email sent successfully! Status code: {response.status_code}")
        return True
    except Exception as e:
        print(f"SendGrid error: {e}")
        return False