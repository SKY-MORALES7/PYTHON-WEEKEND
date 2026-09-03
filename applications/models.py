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
    
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    motivation = models.TextField()
    experience = models.TextField(blank=True)
    expected_attendees = models.PositiveIntegerField(default=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        ordering = ["-id"]
        verbose_name = "Event application"
        verbose_name_plural = "Event applications"

    def __str__(self):
        return f"{self.full_name} - {self.city} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = EventApplication.objects.get(pk=self.pk)
            if old_instance.status != self.status:
                if self.status == 'approved':
                    logger = logging.getLogger(__name__)
                    default_password = "admin123"
                    base_username = slugify(self.email.split('@')[0]) or 'organizer'
                    username = base_username
                    suffix = 0
                    while User.objects.filter(username=username).exists():
                        suffix += 1
                        username = f"{base_username}{suffix}"

                    try:
                        user = User.objects.create_user(
                            username=username,
                            email=self.email,
                            password=default_password,
                            is_staff=True
                        )
                        from django.contrib.contenttypes.models import ContentType
                        from django.contrib.auth.models import Permission

                        group, created = Group.objects.get_or_create(name="Organizers")
                        content_type = ContentType.objects.get_for_model(Event)
                        permissions = Permission.objects.filter(content_type=content_type)
                        group.permissions.set(permissions)
                        user.groups.add(group)

                        Event.objects.create(
                            title=f"Python Weekend - {self.city}",
                            slug=slugify(f"python-weekend-{self.city}-{user.id}"),
                            start_date=timezone.now() + timezone.timedelta(days=60),
                            end_date=timezone.now() + timezone.timedelta(days=62),
                            city=self.city,
                            location=f"{self.city}, {self.country}",
                            owner=user,
                            published=False
                        )
                        try:
                            subject = f"Your organizer account for {getattr(settings, 'SITE_NAME', 'Python Weekend')}"
                            message = (
                                f"Hi {self.full_name},\n\n"
                                f"Your application was approved. You can sign in to manage your event with the following credentials:\n\n"
                                f"Username: {username}\n"
                                f"Password: {default_password}\n\n"
                                f"Please change your password after first login.\n\n"
                                f"Best,\nThe Team"
                            )
                            send_mail(subject=subject, message=message, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[self.email], fail_silently=True)
                        except Exception as e:
                            logger.error(f"Failed to send email: {e}")
                    except Exception as e:
                        logger.error(f"Failed to create user: {e}")

        super().save(*args, **kwargs)


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
        logger = logging.getLogger(__name__)
        from django.contrib.auth.models import User, Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from content.models import EventCoach, EventSponsor

        # Ensure "Organizers" group exists with appropriate restricted permissions
        organizer_group, _ = Group.objects.get_or_create(name="Organizers")
        models_to_grant = [Event, EventCoach, EventSponsor, Form, Question, Answer]
        perms = []
        for model in models_to_grant:
            ct = ContentType.objects.get_for_model(model)
            perms.extend(Permission.objects.filter(content_type=ct))
        organizer_group.permissions.set(perms)

        people = self._get_all_applicants()
        default_password = "admin123"

        for person in people:
            email = person["email"].strip()
            if not email:
                continue
            first_name = person["first_name"].strip()
            last_name = person["last_name"].strip()

            user = User.objects.filter(email=email).first()
            if not user:
                base_username = slugify(first_name.lower() or email.split('@')[0]) or "organizer"
                username = base_username
                num = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{num}"
                    num += 1

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=default_password,
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=True,
                    is_superuser=False
                )
            else:
                user.is_staff = True
                user.save()

            user.groups.add(organizer_group)

            # Only create the draft event for the lead organizer (the first person in the loop)
            if person == people[0]:
                if not Event.objects.filter(owner=user).exists():
                    event_title = f"Python Weekend - {first_name or 'Workshop'}"
                    event_slug = slugify(f"python-weekend-{first_name or 'workshop'}-{user.id}")
                    Event.objects.create(
                        title=event_title,
                        slug=event_slug,
                        start_date=timezone.now() + timezone.timedelta(days=60),
                        end_date=timezone.now() + timezone.timedelta(days=62),
                        location="To be announced",
                        city=first_name or "TBA",
                        owner=user,
                        published=False
                    )

            # Send approval email to applicant
            site_url = getattr(settings, 'SITE_URL', 'https://pythonweekend.org')
            subject = "Your Python Weekend Organizer Application has been Approved!"
            message = (
                f"Hi {first_name or 'Organizer'},\n\n"
                f"Congratulations! Your application to organize a Python Weekend workshop has been approved.\n\n"
                f"You have been granted access to manage your event from the backend.\n\n"
                f"Your Login Details:\n"
                f"Login URL: {site_url}/admin/\n"
                f"Username: {user.username}\n"
                f"Password: {default_password}\n\n"
                f"Please log in to manage your event and update your password.\n\n"
                f"Best,\nThe Python Weekend Team"
            )
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False
                )
            except Exception as e:
                logger.error(f"Failed to send approval email to {email}: {e}")

    def _handle_rejection(self):
        logger = logging.getLogger(__name__)
        people = self._get_all_applicants()

        for person in people:
            email = person["email"].strip()
            if not email:
                continue
            first_name = person["first_name"].strip()

            subject = "Python Weekend Organizer Application Update"
            message = (
                f"Hi {first_name or 'Applicant'},\n\n"
                f"Thank you for your interest in organizing a Python Weekend workshop.\n\n"
                f"After reviewing your application, we regret to inform you that we are unable to approve your application at this time.\n\n"
                f"Best,\nThe Python Weekend Team"
            )
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False
                )
            except Exception as e:
                logger.error(f"Failed to send rejection email to {email}: {e}")

