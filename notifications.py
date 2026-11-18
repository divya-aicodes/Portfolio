from __future__ import annotations

import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from logging import Logger


def send_contact_notification(*, name: str, email: str, message: str, created_at: datetime, logger: Logger) -> bool:
    """Send an optional email alert without making delivery the source of truth."""
    recipient = os.environ.get("NOTIFICATION_EMAIL_TO", "").strip()
    host = os.environ.get("SMTP_HOST", "").strip()
    sender = os.environ.get("SMTP_FROM", "").strip()
    if not all((recipient, host, sender)):
        logger.warning("Contact notification skipped: SMTP is not configured.")
        return False

    email_message = EmailMessage()
    email_message["Subject"] = f"New portfolio message from {name}"
    email_message["From"] = sender
    email_message["To"] = recipient
    email_message["Reply-To"] = email
    email_message.set_content(
        f"New portfolio contact message\n\n"
        f"Name: {name}\nEmail: {email}\nReceived: {created_at.isoformat()}\n\n{message}\n"
    )

    try:
        port = int(os.environ.get("SMTP_PORT", "587"))
        with smtplib.SMTP(host, port, timeout=15) as smtp:
            if os.environ.get("SMTP_USE_TLS", "true").lower() != "false":
                smtp.starttls()
            username = os.environ.get("SMTP_USERNAME", "").strip()
            password = os.environ.get("SMTP_PASSWORD", "")
            if username and password:
                smtp.login(username, password)
            smtp.send_message(email_message)
        return True
    except Exception:
        logger.exception("Contact was saved, but the email notification failed.")
        return False
