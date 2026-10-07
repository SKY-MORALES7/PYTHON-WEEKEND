from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.utils.text import slugify
from django.core.mail import send_mail
import logging

from content.models import Event


# ─────────────────────────────────────────────
#  EVENT APPLICATION
# ─────────────────────────────────────────────

class EventApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="event_applications",
        null=True,
        blank=True,
        help_text="The event applied for"
    )
    form = models.ForeignKey(
        'Form',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_applications"
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = "Event application"
        verbose_name_plural = "Event applications"

    def __str__(self):
        event_title = self.event.title if self.event else "General"
        return f"{self.full_name} - {event_title} ({self.get_status_display()})"


    def send_status_email(self):
        """Dispatches approved or rejected email notifications safely via background thread."""
        import threading
        from django.utils.html import escape
        from core.utils import send_resend_email

        status = self.status
        if status not in ("approved", "rejected") or not self.email:
            return

        site_name = getattr(settings, "SITE_NAME", "Python Weekend")
        site_url = getattr(settings, "SITE_URL", "https://pythonweekend.com").rstrip("/")
        event_name = self.event.title if self.event else "Python Weekend Workshop"
        from_email = settings.DEFAULT_FROM_EMAIL
        applicant_name = self.full_name or "Applicant"
        applicant_email = self.email

        if status == "approved":
            subject = f"Your application for {event_name} has been approved! 🎉"
            text_body = (
                f"Hi {applicant_name},\n\n"
                f"Congratulations! Your application to attend {event_name} has been APPROVED.\n\n"
                f"We are excited to welcome you to the workshop. Our team will follow up with schedule details, "
                f"venue instructions, and prerequisites.\n\n"
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
            <td style="background-color: #16213e; padding: 20px 24px;">
              <span style="color: #FFB800; font-family: monospace; font-size: 13px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Application Approved</span>
              <h2 style="color: #ffffff; margin: 8px 0 0 0; font-size: 20px;">You're in! 🎉</h2>
            </td>
          </tr>
          <tr>
            <td style="padding: 24px; font-size: 15px; line-height: 1.6;">
              <p style="margin: 0 0 16px 0;">Hi <strong>{escape(applicant_name)}</strong>,</p>
              <p style="margin: 0 0 16px 0;">Congratulations! Your application to attend <strong>{escape(event_name)}</strong> has been <strong>approved</strong>.</p>
              <p style="margin: 0 0 16px 0;">We look forward to having you with us. We will follow up with venue details, preparation guidelines, and the full schedule shortly.</p>
              <p style="margin: 0;">Warm regards,<br><strong>The {site_name} Team</strong></p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
        else:
            subject = f"Update regarding your application for {event_name}"
            text_body = (
                f"Hi {applicant_name},\n\n"
                f"Thank you for applying to attend {event_name}.\n\n"
                f"Due to venue capacity constraints, we are unfortunately unable to offer you a seat for this edition.\n\n"
                f"We encourage you to stay connected and apply for future editions or explore our online tutorials.\n\n"
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
            <td style="background-color: #16213e; padding: 20px 24px;">
              <span style="color: #FFB800; font-family: monospace; font-size: 13px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Application Update</span>
              <h2 style="color: #ffffff; margin: 8px 0 0 0; font-size: 20px;">{escape(event_name)}</h2>
            </td>
          </tr>
          <tr>
            <td style="padding: 24px; font-size: 15px; line-height: 1.6;">
              <p style="margin: 0 0 16px 0;">Hi <strong>{escape(applicant_name)}</strong>,</p>
              <p style="margin: 0 0 16px 0;">Thank you for your interest and for taking the time to apply for <strong>{escape(event_name)}</strong>.</p>
              <p style="margin: 0 0 16px 0;">Due to venue capacity constraints, we are unfortunately unable to offer you a seat for this session.</p>
              <p style="margin: 0 0 16px 0;">Please stay tuned for upcoming workshops and feel free to explore our open tutorials.</p>
              <p style="margin: 0;">Warm regards,<br><strong>The {site_name} Team</strong></p>
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
                    recipient_list=[applicant_email],
                    html_message=html_body,
                )
            except Exception as e:
                logging.getLogger(__name__).error(f"Failed to send EventApplication {status} email to {applicant_email}: {e}")

        threading.Thread(target=_send, daemon=True).start()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        if not is_new:
            old_status = EventApplication.objects.filter(pk=self.pk).values_list("status", flat=True).first()

        super().save(*args, **kwargs)

        if not is_new and old_status != self.status and self.status in ("approved", "rejected"):
            self.send_status_email()



# ─────────────────────────────────────────────
#  FORM  (Application form for an event)
# ─────────────────────────────────────────────

class Form(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="application_forms",
        help_text="The event this application form belongs to.",
    )
    text_header = models.CharField(max_length=500, blank=True, help_text="The main heading for the application form.")
    text_description = models.TextField(blank=True, help_text="Detailed description or instructions for the applicants.")
    hero_image = models.ImageField(
        upload_to="forms/heroes/", 
        blank=True, 
        null=True,
        help_text="Optional banner image displayed at the top of the form."
    )
    confirmation_mail = models.TextField(blank=True, help_text="Email text sent to the applicant after submission.")
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Form"
        verbose_name_plural = "Forms"

    def __str__(self):
        return f"Form for {self.event.title}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # Automatically add Name and Email questions by default
            Question.objects.create(
                form=self,
                title="Full Name",
                question_type="text",
                is_required=True,
                order=1
            )
            Question.objects.create(
                form=self,
                title="Email Address",
                question_type="email",
                is_required=True,
                order=2
            )


QUESTION_TYPE_CHOICES = [
    ("text",        "Text (short answer)"),
    ("paragraph",   "Paragraph (long answer)"),
    ("choices",     "Multiple choice"),
    ("email",       "Email"),
    ("url",         "URL"),
    ("number",      "Number"),
]


class Question(models.Model):
    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    title = models.CharField(max_length=500, help_text="The question being asked (e.g. 'What is your current occupation?').")
    help_text = models.CharField(max_length=500, blank=True, help_text="Additional instructions or context for the applicant.")
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        default="text",
        help_text="Determines the input type shown to the applicant."
    )
    choices = models.TextField(blank=True, help_text="Only used if question type is 'Multiple choice'. Enter each option on a new line.")
    is_required = models.BooleanField(default=True, help_text="If checked, the applicant must answer this question.")
    order = models.PositiveSmallIntegerField(default=0, help_text="Lower numbers appear first.")

    class Meta:
        ordering = ["order"]
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self):
        return self.title


class Answer(models.Model):
    application = models.ForeignKey(
        EventApplication,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="answers",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    applicant_email = models.EmailField()
    answer = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "Answer"
        verbose_name_plural = "Answers"

    def __str__(self):
        return f"Answer to '{self.question.title}' by {self.applicant_email}"


WORKSHOP_TYPE_CHOICES = [
    ("remote", "Remote"),
    ("in_person", "In-Person"),
]


class OrganizerApplication(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    lead_first_name = models.CharField(max_length=200)
    lead_last_name = models.CharField(max_length=200, blank=True)
    lead_email = models.EmailField()
    team_members = models.JSONField(default=list, blank=True)

    prerequisites_confirmed = models.BooleanField(default=False)

    workshop_type = models.CharField(
        max_length=20,
        choices=WORKSHOP_TYPE_CHOICES,
        default="in_person",
    )

    commitment_signed = models.BooleanField(default=False)

    has_organized_before = models.BooleanField(default=False)
    previous_event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="returning_organizers",
    )
    target_country = models.CharField(max_length=200, blank=True, help_text="Target country for new organizers")
    target_state = models.CharField(max_length=200, blank=True, help_text="Target state/region for new organizers")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "Organizer application"
        verbose_name_plural = "Organizer applications"

    def __str__(self):
        return f"{self.lead_first_name} {self.lead_last_name} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        if not is_new:
            try:
                old_status = OrganizerApplication.objects.get(pk=self.pk).status
            except OrganizerApplication.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        if not is_new and old_status != self.status:
            if self.status == "approved":
                self._handle_approval()
            elif self.status == "rejected":
                self._handle_rejection()

    def _get_all_applicants(self):
        people = [
            {
                "first_name": self.lead_first_name,
                "last_name": self.lead_last_name,
                "email": self.lead_email
            }
        ]
        if isinstance(self.team_members, list):
            for member in self.team_members:
                if isinstance(member, dict) and member.get("email"):
                    people.append({
                        "first_name": member.get("first_name", ""),
                        "last_name": member.get("last_name", ""),
                        "email": member.get("email", "")
                    })
        return people

    def _handle_approval(self):
        import logging
        import random
        import re
        import threading
        from django.contrib.auth.models import User, Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from django.utils.html import escape
        from core.utils import send_resend_email
        from content.models import EventCoach, EventSponsor, BlogPost, BlogSection
        from tutorials.models import Tutorial
        from coach.models import Coach
        from sponsors.models import Sponsor
        from django.contrib.flatpages.models import FlatPage

        logger = logging.getLogger(__name__)

        # Ensure "Organizers" group exists with permissions to specified models only
        organizer_group, _ = Group.objects.get_or_create(name="Organizers")
        models_to_grant = [
            Coach, FlatPage, BlogPost, BlogSection, Event, EventCoach, EventSponsor,
            Tutorial, Sponsor, Form, Question, Answer, EventApplication
        ]
        perms = []
        for model_cls in models_to_grant:
            try:
                ct = ContentType.objects.get_for_model(model_cls)
                perms.extend(Permission.objects.filter(content_type=ct))
            except Exception as e:
                logger.warning(f"Could not load permissions for {model_cls}: {e}")
        organizer_group.permissions.set(perms)

        people = self._get_all_applicants()
        site_name = getattr(settings, "SITE_NAME", "Python Weekend")
        site_url = getattr(settings, "SITE_URL", "https://pythonweekend.com").rstrip("/")
        from_email = settings.DEFAULT_FROM_EMAIL

        created_users = []
        user_credentials = []

        for idx, person in enumerate(people):
            email = person["email"].strip()
            if not email or "@" not in email:
                continue
            first_name = person["first_name"].strip()
            last_name = person["last_name"].strip()
            is_lead = (idx == 0)

            # Generate random password format: admin + random digits (e.g. admin7294)
            pwd = f"admin{random.randint(1000, 9999)}"

            user = User.objects.filter(email__iexact=email).first()
            if not user:
                # Generate username: first name + 3 random digits (e.g. Sarah482)
                cleaned_first = re.sub(r'[^a-zA-Z]', '', first_name).title() or "Organizer"
                while True:
                    candidate_username = f"{cleaned_first}{random.randint(100, 999)}"
                    if not User.objects.filter(username=candidate_username).exists():
                        username = candidate_username
                        break

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=pwd,
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=True,
                    is_superuser=False
                )
            else:
                user.is_staff = True
                user.is_superuser = False
                user.set_password(pwd)
                if first_name and not user.first_name:
                    user.first_name = first_name
                if last_name and not user.last_name:
                    user.last_name = last_name
                user.save()
                username = user.username

            user.groups.add(organizer_group)
            created_users.append(user)
            user_credentials.append({
                "user": user,
                "email": email,
                "first_name": first_name or user.username,
                "username": user.username,
                "password": pwd,
                "is_lead": is_lead,
            })

        if not created_users:
            return

        # Setup event draft for the lead organizer and attach co-organizers
        lead_user = created_users[0]
        co_users = created_users[1:]

        event = Event.objects.filter(owner=lead_user).first()
        if not event:
            loc_label = self.target_state or self.target_country or lead_user.first_name or "Workshop"
            event_title = f"Python Weekend - {loc_label}"
            base_slug = slugify(f"python-weekend-{loc_label}-{lead_user.id}")
            event_slug = base_slug
            slug_cnt = 1
            while Event.objects.filter(slug=event_slug).exists():
                event_slug = f"{base_slug}-{slug_cnt}"
                slug_cnt += 1

            event = Event.objects.create(
                title=event_title,
                slug=event_slug,
                start_date=timezone.now() + timezone.timedelta(days=60),
                end_date=timezone.now() + timezone.timedelta(days=62),
                location=f"{self.target_state}, {self.target_country}".strip(", ") or "To be announced",
                city=self.target_state or self.target_country or "TBA",
                country=self.target_country or "",
                owner=lead_user,
                published=False
            )

        if co_users:
            event.co_organizers.add(*co_users)

        # Dispatch personalized approval emails in a background thread
        def _send_approval_emails():
            for cred in user_credentials:
                role_label = "Lead Organizer" if cred["is_lead"] else "Co-Organizer"
                subject = f"Your {site_name} Organizer Application has been Approved! 🎉"
                text_body = (
                    f"Hi {cred['first_name']},\n\n"
                    f"Congratulations! Your application to organize a {site_name} workshop has been approved.\n"
                    f"You have been granted backend access as a {role_label}.\n\n"
                    f"Your Admin Login Credentials:\n"
                    f"Login URL: {site_url}/admin/\n"
                    f"Username: {cred['username']}\n"
                    f"Password: {cred['password']}\n\n"
                    f"Please log in to manage your event, view attendee applications, and customize event details. "
                    f"You can change your password anytime in the admin portal.\n\n"
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
                Application Approved
              </span>
              <h1 style="color: #ffffff; margin: 12px 0 0 0; font-size: 22px; font-weight: 800;">Welcome, {escape(role_label)}! 🎉</h1>
            </td>
          </tr>
          <tr>
            <td style="padding: 28px; font-size: 15px; line-height: 1.6; color: #16213e;">
              <p style="margin: 0 0 16px 0;">Hi <strong>{escape(cred['first_name'])}</strong>,</p>
              <p style="margin: 0 0 16px 0;">Congratulations! Your application to organize a <strong>{site_name}</strong> workshop has been approved. You have been granted backend access as a <strong>{escape(role_label)}</strong>.</p>
              <div style="background-color: #f8fafc; border-left: 4px solid #0284c7; padding: 16px 20px; margin: 20px 0; font-size: 14px; color: #16213e;">
                <p style="margin: 0 0 8px 0; font-weight: bold; text-transform: uppercase; font-size: 12px; color: #64748b;">Your Admin Login Details</p>
                <p style="margin: 0 0 4px 0;"><strong>Login URL:</strong> <a href="{site_url}/admin/" style="color: #0284c7;">{site_url}/admin/</a></p>
                <p style="margin: 0 0 4px 0;"><strong>Username:</strong> <code style="background: #e2e8f0; padding: 2px 6px; border-radius: 3px; font-weight: bold;">{escape(cred['username'])}</code></p>
                <p style="margin: 0;"><strong>Password:</strong> <code style="background: #e2e8f0; padding: 2px 6px; border-radius: 3px; font-weight: bold;">{escape(cred['password'])}</code></p>
              </div>
              <p style="margin: 16px 0 0 0;">Please log in to manage your workshop, review applicant responses, and coordinate with your team. You can change your password anytime after logging in.</p>
              <p style="margin: 16px 0 0 0;">Warm regards,<br><strong>The {site_name} Team</strong></p>
            </td>
          </tr>
          <tr>
            <td style="background-color: #f8fafc; padding: 16px 28px; border-top: 2px solid #e2e8f0; font-size: 12px; color: #64748b;">
              Need help? Reply to this email or visit <a href="{site_url}" style="color: #0284c7; font-weight: bold;">{site_url}</a>.
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
                        message=text_body,
                        from_email=from_email,
                        recipient_list=[cred["email"]],
                        html_message=html_body,
                    )
                    logger.info(f"Approval email with credentials sent to {cred['email']}")
                except Exception as e:
                    logger.error(f"Failed to send approval email to {cred['email']}: {e}")

        threading.Thread(target=_send_approval_emails, daemon=True).start()

    def _handle_rejection(self):
        import logging
        import threading
        from django.utils.html import escape
        from core.utils import send_resend_email

        logger = logging.getLogger(__name__)
        people = self._get_all_applicants()
        site_name = getattr(settings, "SITE_NAME", "Python Weekend")
        site_url = getattr(settings, "SITE_URL", "https://pythonweekend.com").rstrip("/")
        from_email = settings.DEFAULT_FROM_EMAIL

        def _send_rejection_emails():
            for person in people:
                email = person["email"].strip()
                if not email or "@" not in email:
                    continue
                first_name = person["first_name"].strip() or "Applicant"

                subject = f"Update regarding your {site_name} Organizer Application"
                text_body = (
                    f"Hi {first_name},\n\n"
                    f"Thank you for your interest and for volunteering to organize a {site_name} workshop.\n\n"
                    f"After carefully reviewing your proposal, we regret to inform you that we are unable to approve your application "
                    f"for this event cycle. We receive applications from communities worldwide and make difficult decisions based on "
                    f"regional capacity and mentor support resources.\n\n"
                    f"We deeply appreciate your passion for Python and encourage you to stay involved in our community.\n\n"
                    f"Warm regards,\nThe {site_name} Team\n"
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
              <span style="background-color: #64748b; color: #ffffff; font-family: monospace; font-size: 11px; font-weight: bold; letter-spacing: 1.5px; text-transform: uppercase; padding: 4px 8px;">
                Application Update
              </span>
              <h1 style="color: #ffffff; margin: 12px 0 0 0; font-size: 22px; font-weight: 800;">Organizer Application Update</h1>
            </td>
          </tr>
          <tr>
            <td style="padding: 28px; font-size: 15px; line-height: 1.6; color: #16213e;">
              <p style="margin: 0 0 16px 0;">Hi <strong>{escape(first_name)}</strong>,</p>
              <p style="margin: 0 0 16px 0;">Thank you for your interest in organizing a <strong>{site_name}</strong> workshop.</p>
              <p style="margin: 0 0 16px 0;">After carefully reviewing your proposal, we regret to inform you that we are unable to approve your application at this time.</p>
              <p style="margin: 16px 0 0 0;">We truly appreciate your support for the community and wish you the best.</p>
              <p style="margin: 16px 0 0 0;">Warm regards,<br><strong>The {site_name} Team</strong></p>
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
                        message=text_body,
                        from_email=from_email,
                        recipient_list=[email],
                        html_message=html_body,
                    )
                    logger.info(f"Rejection email sent to organizer/co-organizer {email}")
                except Exception as e:
                    logger.error(f"Failed to send rejection email to {email}: {e}")

        threading.Thread(target=_send_rejection_emails, daemon=True).start()

