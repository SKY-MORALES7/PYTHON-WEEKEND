from django.db import models


class Sponsor(models.Model):
    TIER_CHOICES = [
        ("platinum", "Platinum"),
        ("gold", "Gold"),
        ("silver", "Silver"),
        ("community", "Community"),
    ]

    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to="sponsors/", blank=True, null=True)
    website = models.URLField(blank=True)
    tagline = models.CharField(max_length=300, blank=True)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default="community")
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["tier", "name"]

    def __str__(self):
        return self.name
