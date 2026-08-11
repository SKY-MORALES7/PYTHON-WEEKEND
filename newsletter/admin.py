from django.contrib import admin
from .models import Newsletter

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("subject", "sent_at", "created_at")
    list_filter = ("sent_at",)
    search_fields = ("subject",)
