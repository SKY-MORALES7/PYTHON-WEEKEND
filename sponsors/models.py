from django.db import models


class Sponsor(models.Model):
    TIER_CHOICES = [
        ("platinum", "Platinum"),
        ("gold", "Gold"),
        ("silver", "Silver"),
        ("community", "Community"),
    ]

    CATEGORY_CHOICES = [
        ("global", "Global Partner"),
        ("event", "Event Partner"),
        ("community_supporter", "Community Supporter"),
    ]

    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to="sponsors/", blank=True, null=True)
    website = models.URLField(blank=True)
    tagline = models.CharField(max_length=300, blank=True)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default="community")
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="community_supporter",
        help_text="Used to group this partner on the Our Partners page."
    )
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["tier", "name"]

    def __str__(self):
        return self.name
