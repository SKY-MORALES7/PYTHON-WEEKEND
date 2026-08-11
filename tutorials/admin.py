from django.contrib import admin
from .models import Tutorial, TutorialSection

class TutorialSectionInline(admin.StackedInline):
    model = TutorialSection
    extra = 1
    fields = ("order", "heading", "body", "code_block", "language")
    ordering = ("order",)

@admin.register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    list_display  = ["title", "resource_type", "difficulty", "estimated_minutes", "published", "created_at"]
    list_editable = ["published"]
    prepopulated_fields = {"slug": ("title",)}
    list_filter  = ["published", "difficulty", "resource_type"]
    search_fields = ["title"]
    inlines = [TutorialSectionInline]
