from django.contrib import admin
from .models import EventApplication


@admin.register(EventApplication)
class EventApplicationAdmin(admin.ModelAdmin):
    # Displays the fields cleanly in columns within your admin dashboard
    list_display = ("full_name", "email", "city", "status")
    
    # Allows you to filter your applications sidebar by status
    list_filter = ("status",)
    
    # Lets you search applications quickly by applicant name or email
    search_fields = ("full_name", "email")
    
    # 🚀 ENHANCEMENT: Changes the status via a dropdown directly in the list table!
    list_editable = ("status",)