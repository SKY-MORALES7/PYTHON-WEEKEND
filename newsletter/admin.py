from django.contrib import admin
from .models import Newsletter, NewsletterSubscriber

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("subject", "sent_at", "created_at")
    list_filter = ("sent_at",)
    search_fields = ("subject",)

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "subscribed_at")
    list_filter = ("is_active",)
    search_fields = ("email",)
