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
    text_header = models.CharField(max_length=500, blank=True)
    text_description = models.TextField(blank=True)
    confirmation_mail = models.TextField(blank=True)
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
    title = models.CharField(max_length=500)
    help_text = models.CharField(max_length=500, blank=True)
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        default="text",
    )
    choices = models.TextField(blank=True)
    is_required = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

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