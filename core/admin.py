from django.contrib import admin
from .models import ContactMessage, Subscriber, Newsletter


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
	list_display = ("name", "email", "interest", "created_at", "read")
	list_filter = ("interest", "read", "created_at")
	search_fields = ("name", "email", "message")
	readonly_fields = ("created_at", "updated_at")


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "subscribed_at")
    list_filter = ("is_active", "subscribed_at")
    search_fields = ("email",)
    readonly_fields = ("subscribed_at",)


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("subject", "sent_at", "created_at")
    list_filter = ("sent_at", "created_at")
    search_fields = ("subject", "content")
    readonly_fields = ("created_at", "updated_at")
