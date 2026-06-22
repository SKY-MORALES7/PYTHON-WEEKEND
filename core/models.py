from django.db import models

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

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}> ({self.interest})"