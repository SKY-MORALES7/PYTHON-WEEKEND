from django.db import models
from core.models import TimeStampedModel

class Subscriber(TimeStampedModel):
    """Stores email addresses for the newsletter."""
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-subscribed_at"]
        db_table = "core_subscriber"

    def __str__(self):
        return self.email
