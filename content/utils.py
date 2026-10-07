import logging
import threading

from django.conf import settings
from django.db import models
from django.utils.html import escape

from core.security import is_email_sending_enabled
from core.utils import send_resend_email

logger = logging.getLogger(__name__)


def send_co_organizer_removal_notification(user, event):
    """
    Sends a branded notification email to a co-organizer when they are deselected
    or removed from an event.
    Also automatically revokes staff status (is_staff = False) if the user has no
    other remaining events they organize or co-organize, preventing unwanted admin access.
    """
    recipient_email = (user.email or "").strip()
    recipient_name = user.first_name or user.username
    event_title = event.title
    site_name = getattr(settings, "SITE_NAME", "Python Weekend")
    site_url = getattr(settings, "SITE_URL", "https://pythonweekend.com").rstrip("/")

    # Check if this user still has any other events they own or co-organize
    from content.models import Event
    has_other_events = Event.objects.filter(
        models.Q(owner=user) | models.Q(co_organizers=user)
    ).exclude(id=event.id).exists()

    # Revoke staff privileges if they have no other events and are not a superuser
    if not has_other_events and not user.is_superuser:
        user.is_staff = False
        user.save(update_fields=["is_staff"])
        logger.info(f"Revoked is_staff for {user.username} as they have no remaining events to manage.")

    if not is_email_sending_enabled():
        logger.info(f"Email sending disabled (EMAIL_ENABLED=False). Skipping removal email to {recipient_email}.")
        return

    if not recipient_email or "@" not in recipient_email:
        logger.warning(f"Cannot send removal notification: {user.username} has no valid email address.")
        return

    subject = f"Update regarding your co-organizer role for {event_title} — {site_name}"
    text_body = (
        f"Hi {recipient_name},\n\n"
        f"This is an automated notification to inform you that your role as a co-organizer for {event_title} has been concluded.\n\n"
        f"As a result, your access to manage this event, view attendee applications, and modify its application forms in the {site_name} admin dashboard has been removed.\n\n"
        f"Thank you for your contributions to the community. If you believe this update was made in error or have questions, please reach out to the lead organizer or the {site_name} team.\n\n"
        f"Best regards,\nThe {site_name} Team\n"
        f"{site_url}\n"
    )

    html_body = f"""<!DOCTYPE html>
<html>
<body style="margin: 0; padding: 24px 12px; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #16213e;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; background-color: #ffffff; border: 3px solid #16213e; box-shadow: 6px 6px 0px #16213e;">
          <tr>
            <td style="background-color: #16213e; padding: 24px 28px;">
              <span style="background-color: #ef4444; color: #ffffff; font-family: monospace; font-size: 11px; font-weight: bold; letter-spacing: 1.5px; text-transform: uppercase; padding: 4px 8px; border: 1.5px solid #16213e;">
                Role Update
              </span>
              <h1 style="color: #ffffff; margin: 12px 0 0 0; font-size: 20px; font-weight: 800;">Co-Organizer Role Concluded</h1>
            </td>
          </tr>
          <tr>
            <td style="padding: 28px; font-size: 15px; line-height: 1.6; color: #16213e;">
              <p style="margin: 0 0 16px 0;">Hi <strong>{escape(recipient_name)}</strong>,</p>
              <p style="margin: 0 0 16px 0;">This email is to notify you that your assignment as a co-organizer for <strong>{escape(event_title)}</strong> has ended.</p>
              <div style="background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 14px 18px; margin: 20px 0; font-size: 14px; color: #991b1b; line-height: 1.5;">
                Your administrative access to manage this event, view attendee applications, and customize event forms in the {site_name} dashboard has been revoked.
              </div>
              <p style="margin: 16px 0 0 0;">Thank you for your time and the contributions you provided to the event. If you believe this removal occurred by mistake, please contact the lead organizer or reply to this message.</p>
              <p style="margin: 20px 0 0 0;">Warm regards,<br><strong>The {site_name} Team</strong></p>
            </td>
          </tr>
          <tr>
            <td style="background-color: #f8fafc; padding: 16px 28px; border-top: 2px solid #e2e8f0; font-size: 12px; color: #64748b;">
              {site_name} — <a href="{site_url}" style="color: #0284c7; text-decoration: underline;">{site_url}</a>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    def _send():
        try:
            send_resend_email(
                subject=subject,
                message=text_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                html_message=html_body,
            )
            logger.info(f"Co-organizer removal notification delivered to {recipient_email} for event '{event_title}'.")
        except Exception as e:
            logger.error(f"Failed to deliver co-organizer removal notification to {recipient_email}: {e}")

    threading.Thread(target=_send, daemon=True).start()
