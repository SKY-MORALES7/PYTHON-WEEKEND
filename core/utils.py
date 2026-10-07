import html
import json
import logging
import re
import threading
import urllib.error
import urllib.request

from django.conf import settings
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired, dumps, loads
from django.urls import reverse
from django.utils.html import escape
from .security import is_email_sending_enabled

logger = logging.getLogger(__name__)


def _sanitize_header(value):
    """Strip CR and LF to prevent email header injection."""
    return re.sub(r"[\r\n]+", " ", str(value or "")).strip()


def send_resend_email(subject, message, from_email, recipient_list, html_message=None, **kwargs):
    """
    Sends email via Resend's HTTPS REST API (https://api.resend.com/emails) over port 443.
    This avoids cloud platform (Render, EC2, Heroku) SMTP port blocks (25, 465, 587)
    and prevents Gunicorn worker timeout kills.
    Falls back to standard Django send_mail if RESEND_API_KEY is not configured.
    """
    api_key = (
        getattr(settings, "RESEND_API_KEY", "")
        or getattr(settings, "EMAIL_HOST_PASSWORD", "")
    ).strip()
    recipients = recipient_list if isinstance(recipient_list, list) else [recipient_list]
    recipients = [str(r).strip() for r in recipients if r and str(r).strip()]
    if not recipients:
        return

    fail_silently = kwargs.get("fail_silently", False)

    if not api_key:
        logger.info(f"No Resend API key found. Falling back to Django send_mail for {recipients}...")
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipients,
            html_message=html_message,
            fail_silently=fail_silently,
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
    if html_message:
        payload["html"] = html_message

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            res_body = response.read().decode("utf-8")
            logger.info(f"Resend HTTP API email sent successfully to {recipients}: {res_body}")
    except urllib.error.HTTPError as e:
        err_detail = e.read().decode("utf-8", errors="ignore")
        logger.error(f"Resend HTTP API returned HTTP {e.code}: {err_detail}. Falling back to send_mail...")
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipients,
                html_message=html_message,
                fail_silently=fail_silently,
            )
        except Exception as fallback_err:
            logger.error(f"Fallback send_mail also failed: {fallback_err}")
            raise RuntimeError(f"Resend HTTP API error ({e.code}): {err_detail}")
    except Exception as e:
        logger.error(f"Failed to send via Resend HTTP API ({e}). Falling back to send_mail...")
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipients,
            html_message=html_message,
            fail_silently=fail_silently,
        )


# ─── Newsletter Unsubscribe Helpers ──────────────────────────────────────────

def generate_unsubscribe_token(email):
    """Generate a tamper-proof signed token encoding the subscriber's email."""
    clean_email = email.strip().lower()
    return dumps(clean_email, salt="pw-newsletter-unsub")


def verify_unsubscribe_token(token, max_age=60 * 60 * 24 * 365):
    """
    Verify and decode the signed unsubscribe token.
    Defaults to 1 year validity. Returns email if valid, or None.
    """
    if not token:
        return None
    try:
        email = loads(token, salt="pw-newsletter-unsub", max_age=max_age)
        return str(email).strip().lower()
    except (BadSignature, SignatureExpired, Exception) as e:
        logger.warning(f"Invalid or expired unsubscribe token: {e}")
        return None


def get_unsubscribe_url(email, request=None):
    """Build the absolute URL for 1-click unsubscribe."""
    token = generate_unsubscribe_token(email)
    try:
        path = reverse("core:newsletter_unsubscribe_token", kwargs={"token": token})
    except Exception:
        path = f"/newsletter/unsubscribe/{token}/"

    if request:
        return request.build_absolute_uri(path)

    site_url = getattr(settings, "SITE_URL", "https://pythonweekend.org").rstrip("/")
    return f"{site_url}{path}"


def format_newsletter_content(raw_content, unsubscribe_url):
    """
    Formats newsletter content into plain text and rich HTML,
    ensuring 'Click here to unsubscribe' (with 'here' as the link) is always present.
    """
    site_name = getattr(settings, "SITE_NAME", "Python Weekend")

    # 1. Plain text format
    text_message = (
        f"{raw_content.strip()}\n\n"
        f"----------------------------------------\n"
        f"You are receiving this email because you subscribed to {site_name} Dispatch.\n"
        f"Click here to unsubscribe: {unsubscribe_url}\n"
    )

    # 2. HTML format
    # If the author used HTML tags, preserve them; otherwise convert newlines to paragraphs
    if "<p>" in raw_content or "<br>" in raw_content or "<div>" in raw_content:
        body_html = raw_content
    else:
        paragraphs = [p.strip() for p in raw_content.split("\n\n") if p.strip()]
        body_html = "".join(f"<p style='margin: 0 0 16px 0; line-height: 1.6;'>{escape(p).replace(chr(10), '<br>')}</p>" for p in paragraphs)

    html_message = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{site_name} Dispatch</title>
</head>
<body style="margin: 0; padding: 24px 12px; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #16213e;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 620px; background-color: #ffffff; border: 3px solid #16213e; box-shadow: 6px 6px 0px #16213e;">
          <!-- Header Banner -->
          <tr>
            <td style="background-color: #16213e; padding: 24px 28px; border-bottom: 3px solid #16213e;">
              <span style="display: inline-block; background-color: #0284c7; color: #ffffff; font-family: monospace; font-size: 11px; font-weight: bold; letter-spacing: 1.5px; text-transform: uppercase; padding: 4px 8px; border: 1.5px solid #16213e;">
                Dispatch Newsletter
              </span>
              <h1 style="color: #ffffff; margin: 12px 0 0 0; font-size: 24px; font-weight: 800; text-transform: uppercase; letter-spacing: -0.5px;">
                {site_name}
              </h1>
            </td>
          </tr>

          <!-- Main Content -->
          <tr>
            <td style="padding: 28px; font-size: 15px; line-height: 1.6; color: #16213e;">
              {body_html}
            </td>
          </tr>

          <!-- Footer with Unsubscribe -->
          <tr>
            <td style="background-color: #f8fafc; padding: 20px 28px; border-top: 2px solid #e2e8f0; font-size: 12px; color: #64748b; line-height: 1.6;">
              <p style="margin: 0 0 8px 0;">
                You are receiving this update because you subscribed to the <strong>{site_name} Dispatch</strong>.
              </p>
              <p style="margin: 0;">
                Don't want to receive these emails? Click <a href="{unsubscribe_url}" style="color: #0284c7; text-decoration: underline; font-weight: bold;">here</a> to unsubscribe.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    return text_message, html_message


def send_newsletter_broadcast(newsletter, request=None):
    """
    Delivers a newsletter to all active subscribers.
    Each subscriber receives a personalized unsubscribe link.
    Runs asynchronously in a background thread to prevent blocking requests.
    """
    from subscribers.models import Subscriber
    from django.utils import timezone

    if not is_email_sending_enabled():
        logger.info("Email sending disabled via EMAIL_ENABLED=False. Skipping newsletter broadcast.")
        return 0

    active_subscribers = list(
        Subscriber.objects.filter(is_active=True).values_list("email", flat=True)
    )
    if not active_subscribers:
        logger.info(f"No active subscribers found for newsletter '{newsletter.subject}'.")
        return 0

    site_url = getattr(settings, "SITE_URL", "https://pythonweekend.org").rstrip("/")
    if request:
        base_url = request.build_absolute_uri("/").rstrip("/")
    else:
        base_url = site_url

    def _broadcast_worker():
        sent_count = 0
        from_email = settings.DEFAULT_FROM_EMAIL
        for sub_email in active_subscribers:
            try:
                token = generate_unsubscribe_token(sub_email)
                unsub_url = f"{base_url}/newsletter/unsubscribe/{token}/"
                text_msg, html_msg = format_newsletter_content(newsletter.content, unsub_url)

                send_resend_email(
                    subject=newsletter.subject,
                    message=text_msg,
                    from_email=from_email,
                    recipient_list=[sub_email],
                    html_message=html_msg,
                )
                sent_count += 1
            except Exception as err:
                logger.error(f"Failed to deliver newsletter '{newsletter.subject}' to {sub_email}: {err}")

        logger.info(f"Broadcast completed for '{newsletter.subject}': successfully sent to {sent_count}/{len(active_subscribers)} subscribers.")

    thread = threading.Thread(target=_broadcast_worker, daemon=True)
    thread.start()

    # Mark as sent immediately
    newsletter.sent_at = timezone.now()
    newsletter.save(update_fields=["sent_at"])
    return len(active_subscribers)


# ─── Contact Form Notification ───────────────────────────────────────────────

def _deliver_contact_notifications(name, email, interest, message):
    """Worker function executed in a background thread."""
    site_name = getattr(settings, "SITE_NAME", "Python Weekend")
    from_email = settings.DEFAULT_FROM_EMAIL

    # 1. Confirmation email to the submitter (so they know their message went through)
    user_subject = f"We received your message — {site_name}"
    user_text = (
        f"Hi {name},\n\n"
        f"Thank you for contacting {site_name}! We have received your message regarding '{interest.title()}':\n\n"
        f"\"{message}\"\n\n"
        f"Our team will review your inquiry and get back to you shortly.\n\n"
        f"Best regards,\nThe {site_name} Team\n"
        f"{getattr(settings, 'SITE_URL', 'https://pythonweekend.org')}\n"
    )
    user_html = f"""<!DOCTYPE html>
<html>
<body style="margin: 0; padding: 24px 12px; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #16213e;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; background-color: #ffffff; border: 3px solid #16213e; box-shadow: 6px 6px 0px #16213e;">
          <tr>
            <td style="background-color: #16213e; padding: 20px 24px;">
              <span style="color: #FFB800; font-family: monospace; font-size: 13px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">{site_name}</span>
              <h2 style="color: #ffffff; margin: 8px 0 0 0; font-size: 20px;">Thank you for reaching out!</h2>
            </td>
          </tr>
          <tr>
            <td style="padding: 24px; font-size: 15px; line-height: 1.6;">
              <p style="margin: 0 0 16px 0;">Hi <strong>{escape(name)}</strong>,</p>
              <p style="margin: 0 0 16px 0;">We've received your inquiry regarding <strong>{escape(interest.title())}</strong>.</p>
              <div style="background-color: #f8fafc; border-left: 4px solid #0284c7; padding: 12px 16px; margin: 16px 0; font-size: 14px; color: #334155;">
                {escape(message).replace(chr(10), '<br>')}
              </div>
              <p style="margin: 16px 0 0 0;">Our team will review your message and get back to you as soon as possible.</p>
            </td>
          </tr>
          <tr>
            <td style="background-color: #f8fafc; padding: 16px 24px; border-top: 1px solid #e2e8f0; font-size: 13px; color: #64748b;">
              Best regards,<br>
              <strong>The {site_name} Team</strong>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    try:
        send_resend_email(
            subject=user_subject,
            message=user_text,
            from_email=from_email,
            recipient_list=[email],
            html_message=user_html,
        )
        logger.info(f"Contact confirmation sent to submitter {email}")
    except Exception as e:
        logger.error(f"Failed to send contact confirmation to {email}: {e}")

    # 2. Alert to internal staff / superusers
    from django.contrib.auth import get_user_model
    User = get_user_model()
    target_team = []
    custom_inbox = getattr(settings, "CONTACT_NOTIFICATION_EMAIL", "").strip()
    if custom_inbox:
        target_team.append(custom_inbox)

    superuser_emails = list(
        User.objects.filter(is_superuser=True, is_active=True)
        .exclude(email="")
        .exclude(email__endswith="@example.com")
        .values_list("email", flat=True)
    )
    for s_email in superuser_emails:
        if s_email not in target_team:
            target_team.append(s_email)

    if not target_team:
        target_team = [from_email]

    staff_subject = f"New Contact Form Submission [{interest.upper()}]: {name}"
    staff_body = (
        f"A new contact message has been submitted on {site_name}.\n\n"
        f"Details:\n"
        f"- Name: {name}\n"
        f"- Email: {email}\n"
        f"- Interest: {interest}\n\n"
        f"Message:\n{message}\n\n"
        f"---\n"
        f"Submitted via the website contact form."
    )

    try:
        send_resend_email(
            subject=staff_subject,
            message=staff_body,
            from_email=from_email,
            recipient_list=target_team,
        )
        logger.info(f"Staff contact alert sent for submission from {email}")
    except Exception as e:
        logger.error(f"Failed to send staff contact alert: {e}")


def send_contact_notifications(contact_submission):
    """
    Asynchronously delivers contact form acknowledgment to the inquirer
    and notification alert to staff.
    """
    if not is_email_sending_enabled():
        logger.info("Outbound emails disabled via EMAIL_ENABLED=False. Skipping contact notifications.")
        return

    user_email = _sanitize_header(contact_submission.email)
    user_name = _sanitize_header(getattr(contact_submission, "name", getattr(contact_submission, "full_name", "Friend")))
    interest = _sanitize_header(getattr(contact_submission, "interest", "general")).lower()
    user_message = getattr(contact_submission, "message", "")

    if not user_email or "@" not in user_email:
        return

    thread = threading.Thread(
        target=_deliver_contact_notifications,
        args=(user_name, user_email, interest, user_message),
        daemon=True,
    )
    thread.start()
    logger.info(f"Contact notification worker started for {user_email}")


# ─── Newsletter Welcome ──────────────────────────────────────────────────────

def _deliver_newsletter_welcome(email, request=None):
    """Send welcome email with personalized unsubscribe link in a background thread."""
    site_name = getattr(settings, "SITE_NAME", "Python Weekend")
    unsub_url = get_unsubscribe_url(email, request=request)

    subject = f"Welcome to the {site_name} Dispatch!"
    message_body = (
        f"Hello!\n\n"
        f"Thank you for subscribing to the {site_name} newsletter.\n\n"
        f"You will now receive the latest updates, event announcements, and "
        f"opportunities directly in your inbox.\n\n"
        f"Best regards,\nThe {site_name} Team\n\n"
        f"----------------------------------------\n"
        f"Click here to unsubscribe: {unsub_url}\n"
    )

    html_message = f"""<!DOCTYPE html>
<html>
<body style="margin: 0; padding: 24px 12px; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #16213e;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; background-color: #ffffff; border: 3px solid #16213e; box-shadow: 6px 6px 0px #16213e;">
          <tr>
            <td style="background-color: #16213e; padding: 24px 28px;">
              <span style="background-color: #0284c7; color: #ffffff; font-family: monospace; font-size: 11px; font-weight: bold; letter-spacing: 1.5px; text-transform: uppercase; padding: 4px 8px; border: 1.5px solid #16213e;">
                Welcome
              </span>
              <h1 style="color: #ffffff; margin: 12px 0 0 0; font-size: 24px; font-weight: 800;">Welcome to the {site_name} Dispatch!</h1>
            </td>
          </tr>
          <tr>
            <td style="padding: 28px; font-size: 15px; line-height: 1.6; color: #16213e;">
              <p style="margin: 0 0 16px 0;">Hello!</p>
              <p style="margin: 0 0 16px 0;">Thank you for subscribing to the <strong>{site_name}</strong> newsletter.</p>
              <p style="margin: 0 0 16px 0;">You'll receive periodic updates, event announcements, tutorials, and community highlights straight to your inbox.</p>
              <p style="margin: 0;">Warm regards,<br><strong>The {site_name} Team</strong></p>
            </td>
          </tr>
          <tr>
            <td style="background-color: #f8fafc; padding: 20px 28px; border-top: 2px solid #e2e8f0; font-size: 12px; color: #64748b; line-height: 1.6;">
              Don't want to receive these emails? Click <a href="{unsub_url}" style="color: #0284c7; text-decoration: underline; font-weight: bold;">here</a> to unsubscribe.
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    try:
        send_resend_email(
            subject=subject,
            message=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
        )
        logger.info(f"Newsletter welcome sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send newsletter welcome email: {e}")


def send_newsletter_welcome(email, request=None):
    """Starts the welcome email in a background thread."""
    if not is_email_sending_enabled():
        logger.info("Outbound email sending is globally disabled via EMAIL_ENABLED=False. Skipping newsletter welcome.")
        return

    clean_email = _sanitize_header(email)
    if not clean_email or "@" not in clean_email:
        return

    api_key = (getattr(settings, "RESEND_API_KEY", "") or getattr(settings, "EMAIL_HOST_PASSWORD", "")).strip()
    if not api_key:
        logger.warning("Newsletter welcome skipped: RESEND_API_KEY / EMAIL_HOST_PASSWORD is empty or unset.")
        return

    thread = threading.Thread(
        target=_deliver_newsletter_welcome,
        args=(clean_email, request),
        daemon=True,
    )
    thread.start()
    logger.info(f"Newsletter welcome email queued for {clean_email}")