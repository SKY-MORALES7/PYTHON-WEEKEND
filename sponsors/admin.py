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
    list_display  = ["name", "tier", "category", "active"]
    list_editable = ["active", "category"]
    list_filter   = ["tier", "category", "active"]
    search_fields = ["name", "tagline"]
