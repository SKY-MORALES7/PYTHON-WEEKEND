import logging
import threading

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.html import escape

from core.utils import send_resend_email

logger = logging.getLogger(__name__)

# Create your models here.

class TimeStampedModel(models.Model):
    """Abstract base model for created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ContactMessage(TimeStampedModel):
    """Stores submissions from the public contact form."""

    INTEREST_ATTEND = "attend"
    INTEREST_COACH = "coach"
    INTEREST_SPONSOR = "sponsor"
    INTEREST_OTHER = "other"

    INTEREST_CHOICES = [
        (INTEREST_ATTEND, "Attend an event"),
        (INTEREST_COACH, "Volunteer as a coach"),
        (INTEREST_SPONSOR, "Sponsor Python Weekend"),
        (INTEREST_OTHER, "Something else"),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    interest = models.CharField(max_length=30, choices=INTEREST_CHOICES, default=INTEREST_OTHER)
    message = models.TextField()
    read = models.BooleanField(default=False, help_text="Mark when the message has been reviewed")
    reply = models.TextField(
        blank=True,
        help_text="Type a reply here and save to send an email response to the sender."
    )
    replied_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the last reply was sent"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}> ({self.interest})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_reply = ""
        if not is_new:
            old_reply = ContactMessage.objects.filter(pk=self.pk).values_list("reply", flat=True).first() or ""

        new_reply = (self.reply or "").strip()
        should_send = bool(new_reply and new_reply != (old_reply or "").strip())

        if should_send:
            self.read = True
            self.replied_at = timezone.now()

        super().save(*args, **kwargs)

        if should_send:
            self.send_reply_email()

    def send_reply_email(self):
        site_name = getattr(settings, "SITE_NAME", "Python Weekend")
        site_url = getattr(settings, "SITE_URL", "https://pythonweekend.org").rstrip("/")
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_email = self.email
        recipient_name = self.name or "there"
        reply_content = self.reply.strip()
        orig_msg = self.message.strip()

        subject = f"Re: Your message to {site_name}"
        text_body = (
            f"Hi {recipient_name},\n\n"
            f"Thank you for contacting {site_name}.\n\n"
            f"{reply_content}\n\n"
            f"--- Original Message ---\n"
            f"{orig_msg}\n\n"
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
              <span style="background-color: #0284c7; color: #ffffff; font-family: monospace; font-size: 11px; font-weight: bold; letter-spacing: 1.5px; text-transform: uppercase; padding: 4px 8px; border: 1.5px solid #16213e;">
                Response to Your Inquiry
              </span>
              <h1 style="color: #ffffff; margin: 12px 0 0 0; font-size: 20px; font-weight: 800;">{escape(site_name)}</h1>
            </td>
          </tr>
          <tr>
            <td style="padding: 28px; font-size: 15px; line-height: 1.6; color: #16213e;">
              <p style="margin: 0 0 16px 0;">Hi <strong>{escape(recipient_name)}</strong>,</p>
              <div style="background-color: #f8fafc; border-left: 4px solid #0284c7; padding: 16px; margin: 16px 0; font-size: 15px; color: #1e293b; white-space: pre-wrap;">{escape(reply_content)}</div>
              <p style="margin: 24px 0 8px 0; font-size: 13px; font-weight: bold; color: #64748b; text-transform: uppercase;">Your Original Message:</p>
              <div style="background-color: #f1f5f9; padding: 12px 16px; border-radius: 4px; font-size: 13px; color: #475569; white-space: pre-wrap;">{escape(orig_msg)}</div>
              <p style="margin: 24px 0 0 0;">Warm regards,<br><strong>The {site_name} Team</strong></p>
            </td>
          </tr>
          <tr>
            <td style="background-color: #f8fafc; padding: 16px 28px; border-top: 2px solid #e2e8f0; font-size: 12px; color: #64748b;">
              Visit us at <a href="{site_url}" style="color: #0284c7; font-weight: bold;">{site_url}</a>.
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
                    from_email=from_email,
                    recipient_list=[recipient_email],
                    html_message=html_body,
                )
                logger.info(f"ContactMessage reply sent to {recipient_email}")
            except Exception as e:
                logger.error(f"Failed to send ContactMessage reply to {recipient_email}: {e}")

        threading.Thread(target=_send, daemon=True).start()

