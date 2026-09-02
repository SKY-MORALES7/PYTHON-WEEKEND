import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def send_contact_notifications(contact_submission):
    """
    Routes general contact form inquiries from the core app directly 
    to relevant departments (Sponsors, Coaches, Attendees/Organizers).
    """
    site_name = getattr(settings, 'SITE_NAME', 'Python Weekend')
    
    user_email = contact_submission.email
    user_name = getattr(contact_submission, 'name', getattr(contact_submission, 'full_name', 'Inquirer'))
    interest = getattr(contact_submission, 'interest', 'general').lower()
    user_message = getattr(contact_submission, 'message', '')

    from django.contrib.auth import get_user_model
    User = get_user_model()
    target_team = list(User.objects.filter(is_superuser=True, is_active=True).exclude(email='').values_list('email', flat=True))
    if not target_team:
        target_team = [settings.DEFAULT_FROM_EMAIL]
    
    if "sponsor" in interest:
        team_label = "Sponsorship Team"
    elif "coach" in interest:
        team_label = "Coaching Team"
    else:
        team_label = "Event Organizing Team"

    # 1. Message configuration for the user
    user_subject = f"Thank you for reaching out to {site_name}"
    user_message_body = (
        f"Hi {user_name},\n\n"
        f"Thank you for contacting us! We've received your inquiry regarding your interest in: '{interest}'. "
        f"Your message has been forwarded to our {team_label}.\n\n"
        f"We will review your message and get back to you shortly.\n\n"
        f"Best regards,\nThe {site_name} Team"
    )

    # 2. Message configuration for internal team alerts
    staff_subject = f"New Core Contact Form Submission [{interest.upper()}]"
    staff_message_body = (
        f"A new contact message has been submitted.\n\n"
        f"Details:\n"
        f"- Name: {user_name}\n"
        f"- Email: {user_email}\n"
        f"- Interest: {interest}\n\n"
        f"Message:\n{user_message}\n"
    )

    try:
        # Deliver copy to the submitter
        send_mail(
            subject=user_subject,
            message=user_message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )

        # Deliver alert to internal departments
        if target_team:
            send_mail(
                subject=staff_subject,
                message=staff_message_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=target_team,
                fail_silently=False,
            )
            
    except Exception as e:
        logger.error(f"Failed to execute core app contact email routing: {e}")

def send_newsletter_welcome(email):
    """
    Sends a welcome email to new newsletter subscribers.
    """
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
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Failed to send newsletter welcome email: {e}")