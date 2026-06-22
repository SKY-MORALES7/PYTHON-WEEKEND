from django.db import models


class Coach(models.Model):
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="coaches/", blank=True, null=True)
    github = models.URLField(blank=True)
    linkedIn = models.URLField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

