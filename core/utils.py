import logging
import re
from django.core.mail import send_mail
from django.conf import settings
from .security import is_email_sending_enabled

logger = logging.getLogger(__name__)


def _sanitize_header(value):
    """Strip CR and LF to prevent email header injection."""
    return re.sub(r"[\r\n]+", " ", str(value or "")).strip()


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
            send_mail(
                subject=staff_subject,
                message=staff_message_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=target_team,
                fail_silently=False,
            )
            logger.info(f"Staff contact notification sent for submission from {user_email}")
    except Exception as e:
        logger.error(f"Failed to execute core app contact email routing: {e}")


def send_newsletter_welcome(email):
    """
    Sends a welcome email to new newsletter subscribers.
    Wrapped with the email sending kill-switch.
    """
    if not is_email_sending_enabled():
        logger.info("Outbound email sending is globally disabled via EMAIL_ENABLED=False. Skipping newsletter welcome.")
        return

    clean_email = _sanitize_header(email)
    if not clean_email or "@" not in clean_email:
        return

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
        send_mail(
            subject=subject,
            message=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[clean_email],
            fail_silently=False,
        )
        logger.info(f"Newsletter welcome sent to {clean_email}")
    except Exception as e:
        logger.error(f"Failed to send newsletter welcome email: {e}")