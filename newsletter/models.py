from django.db import models
from core.models import TimeStampedModel

class Newsletter(TimeStampedModel):
    """Stores newsletter content to be sent to subscribers."""
    subject = models.CharField(max_length=255)
    content = models.TextField()
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "core_newsletter"

    def __str__(self):
        return self.subject

from subscribers.models import Subscriber

class NewsletterSubscriber(Subscriber):
    class Meta:
        proxy = True
        verbose_name = "Subscriber"
        verbose_name_plural = "Subscribers"
