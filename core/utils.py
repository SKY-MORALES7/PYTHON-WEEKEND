import json
import logging
import re
import threading
import urllib.error
import urllib.request

from django.conf import settings
from django.core.mail import send_mail
from .security import is_email_sending_enabled

logger = logging.getLogger(__name__)


def _sanitize_header(value):
    """Strip CR and LF to prevent email header injection."""
    return re.sub(r"[\r\n]+", " ", str(value or "")).strip()


def send_resend_email(subject, message, from_email, recipient_list):
    """
    Sends email via Resend's HTTPS REST API (https://api.resend.com/emails) over port 443.
    This avoids cloud platform (Render, EC2, Heroku) SMTP port blocks (25, 465, 587)
    and prevents Gunicorn worker timeout kills.
    Falls back to standard Django send_mail if RESEND_API_KEY is not configured.
    """
    api_key = (getattr(settings, "RESEND_API_KEY", "") or getattr(settings, "EMAIL_HOST_PASSWORD", "")).strip()
    recipients = recipient_list if isinstance(recipient_list, list) else [recipient_list]
    recipients = [r for r in recipients if r]
    if not recipients:
        return

    if not api_key:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipients,
            fail_silently=False,
        )
        return

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Python-Weekend-App/1.0",
    }

    payload = {
        "from": from_email,
        "to": recipients,
        "subject": subject,
        "text": message,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode("utf-8")
            logger.info(f"Resend HTTP API email sent successfully to {recipients}: {res_body}")
    except urllib.error.HTTPError as e:
        err_detail = e.read().decode("utf-8", errors="ignore")
        logger.error(f"Resend HTTP API returned HTTP {e.code}: {err_detail}")
        raise RuntimeError(f"Resend HTTP API error ({e.code}): {err_detail}")
    except Exception as e:
        logger.error(f"Failed to send via Resend HTTP API ({e}). Falling back to send_mail...")
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipients,
            fail_silently=False,
        )


def send_contact_notifications(contact_submission):
    """
    Routes general contact form inquiries from the core app directly 
    to relevant departments (Sponsors, Coaches, Attendees/Organizers).
    
    SECURITY HARDENING:
    - Does NOT send an automated confirmation to user_email. This prevents
      the contact form from being abused as an open email reflection / mail-bomb proxy.
    - Sends an alert ONLY to verified internal administrators / superusers.
    - Subject and sender headers are strictly sanitized against injection.
    """
    if not is_email_sending_enabled():
        logger.info("Outbound email sending is globally disabled via EMAIL_ENABLED=False. Skipping contact notification.")
        return

    user_email = _sanitize_header(contact_submission.email)
    user_name = _sanitize_header(getattr(contact_submission, 'name', getattr(contact_submission, 'full_name', 'Inquirer')))
    interest = _sanitize_header(getattr(contact_submission, 'interest', 'general')).lower()
    user_message = getattr(contact_submission, 'message', '')

    from django.contrib.auth import get_user_model
    User = get_user_model()
    target_team = list(User.objects.filter(is_superuser=True, is_active=True).exclude(email='').values_list('email', flat=True))
    if not target_team:
        target_team = [settings.DEFAULT_FROM_EMAIL]

    # Staff alert message configuration
    staff_subject = f"New Core Contact Form Submission [{interest.upper()}]: {user_name}"
    staff_message_body = (
        f"A new contact message has been submitted on Python Weekend.\n\n"
        f"Details:\n"
        f"- Name: {user_name}\n"
        f"- Email: {user_email}\n"
        f"- Interest: {interest}\n\n"
        f"Message:\n{user_message}\n\n"
        f"---\n"
        f"Submitted via the website contact form."
    )

    try:
        if target_team:
            send_resend_email(
                subject=staff_subject,
                message=staff_message_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=target_team,
            )
            logger.info(f"Staff contact notification sent for submission from {user_email}")
    except Exception as e:
        logger.error(f"Failed to execute core app contact email routing: {e}")


def _deliver_newsletter_welcome(email):
    """Send the welcome email in a background thread so the signup request is never blocked."""
    site_name = getattr(settings, 'SITE_NAME', 'Python Weekend')
    subject = f"Welcome to the {site_name} Dispatch!"
    message_body = (
        f"Hello!\n\n"
        f"Thank you for subscribing to the {site_name} newsletter.\n\n"
        f"You will now receive the latest updates, event announcements, and "
        f"opportunities directly in your inbox.\n\n"
        f"Best regards,\nThe {site_name} Team"
    )

    try:
        send_resend_email(
            subject=subject,
            message=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        logger.info(f"Newsletter welcome sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send newsletter welcome email: {e}")


def send_newsletter_welcome(email):
    """
    Starts the welcome email in a background thread so the signup request returns immediately.
    Wrapped with the email sending kill-switch.
    """
    if not is_email_sending_enabled():
        logger.info("Outbound email sending is globally disabled via EMAIL_ENABLED=False. Skipping newsletter welcome.")
        return

    clean_email = _sanitize_header(email)
    if not clean_email or "@" not in clean_email:
        return

    api_key = (getattr(settings, "RESEND_API_KEY", "") or getattr(settings, "EMAIL_HOST_PASSWORD", "")).strip()
    if not api_key:
        logger.warning("Newsletter welcome skipped: RESEND_API_KEY is empty or unset.")
        return

    thread = threading.Thread(
        target=_deliver_newsletter_welcome,
        args=(clean_email,),
        daemon=True,
    )
    thread.start()
    logger.info(f"Newsletter welcome email queued for {clean_email}")