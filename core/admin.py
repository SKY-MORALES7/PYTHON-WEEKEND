from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
	list_display = ("name", "email", "interest", "created_at", "read")
	list_filter = ("interest", "read", "created_at")
	search_fields = ("name", "email", "message")
	readonly_fields = ("created_at", "updated_at")
