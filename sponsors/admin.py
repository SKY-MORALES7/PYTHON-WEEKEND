# from django.contrib import admin
# from .models import Sponsor


# @admin.register(Sponsor)
# class SponsorAdmin(admin.ModelAdmin):
#     list_display = ("name", "event")
#     search_fields = ("name",)

from django.contrib import admin
from .models import Sponsor

@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ["name", "tier", "active"]
    list_editable = ["active"]
    list_filter = ["tier"]
    search_fields = ["name"]
