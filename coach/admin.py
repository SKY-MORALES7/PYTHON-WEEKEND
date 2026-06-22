from django.contrib import admin
from .models import Coach

@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ["name", "role", "active"]
    list_editable = ["active"]
    search_fields = ["name"]