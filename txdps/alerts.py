"""Notification helpers."""
import logging
import os

import sendgrid
import twilio.rest


def notify_phone(msg: str, phone_number: int):
    """Send a text containing the given message to the given phone number."""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    origin_phone = os.getenv("TWILIO_PHONE_NUMBER")
    client = twilio.rest.Client(account_sid, auth_token)
    final_phone = f"+1{phone_number}"
    message = client.messages.create(body=msg, from_=origin_phone, to=final_phone)
    logging.info(f"Sent SMS to {final_phone}")
    return message


def notify_email(msg: str, email_address: str, subject: str):
    """Send an email containing the given message to the given email address."""
    client = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))
    from_email = sendgrid.helpers.mail.Email(email_address)
    to_email = sendgrid.helpers.mail.To(email_address)
    html_msg = f"""
<html>
<body>
<pre style="font: monospace">
{msg}
</pre>
</body>
</html>
"""
    content = sendgrid.helpers.mail.Content("text/html", html_msg)
    mail = sendgrid.helpers.mail.Mail(from_email, to_email, subject, content)
    response = client.client.mail.send.post(request_body=mail.get())
    if response.status_code < 200 or response.status_code >= 300:
        raise ValueError(f"Failed to send email: {response.body}")
    logging.info(f"Sent email to {email_address}")
    return response
