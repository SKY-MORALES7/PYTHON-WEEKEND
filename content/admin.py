from django.contrib import admin
from .models import BlogPost, BlogSection, Tutorial, TutorialSection, Event


# ─────────────────────────────────────────────
#  BLOG
# ─────────────────────────────────────────────

class BlogSectionInline(admin.StackedInline):
    model = BlogSection
    extra = 1
    fields = ("order", "heading", "body", "code_block", "language")
    ordering = ("order",)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display  = ["title", "author", "published", "published_at"]
    list_editable = ["published"]
    prepopulated_fields = {"slug": ("title",)}
    list_filter  = ["published"]
    search_fields = ["title", "author"]
    inlines = [BlogSectionInline]

    fieldsets = (
        ("Post info", {
            "fields": ("title", "slug", "author", "published", "published_at")
        }),
        ("Cover image", {
            "fields": ("cover_image",),
            "classes": ("collapse",),
        }),
        ("Excerpt", {
            "fields": ("excerpt",),
            "description": "Short summary shown on the blog card."
        }),
        ("Legacy content (optional)", {
            "fields": ("content",),
            "classes": ("collapse",),
            "description": (
                "Leave this blank and use the Sections below instead. "
                "Only kept for backwards compatibility."
            ),
        }),
    )


# ─────────────────────────────────────────────
#  TUTORIAL
# ─────────────────────────────────────────────

class TutorialSectionInline(admin.StackedInline):
    model = TutorialSection
    extra = 1
    fields = ("order", "heading", "body", "code_block", "language")
    ordering = ("order",)


@admin.register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    list_display  = ["title", "difficulty", "estimated_minutes", "published", "created_at"]
    list_editable = ["published"]
    prepopulated_fields = {"slug": ("title",)}
    list_filter  = ["published", "difficulty"]
    search_fields = ["title"]
    inlines = [TutorialSectionInline]

    fieldsets = (
        ("Tutorial info", {
            "fields": ("title", "slug", "difficulty", "estimated_minutes", "published")
        }),
        ("Cover image", {
            "fields": ("cover_image",),
            "classes": ("collapse",),
        }),
        ("Excerpt", {
            "fields": ("excerpt",),
            "description": "Short summary shown on the tutorial card."
        }),
        ("Legacy content (optional)", {
            "fields": ("content",),
            "classes": ("collapse",),
            "description": (
                "Leave this blank and use the Sections below instead. "
                "Only kept for backwards compatibility."
            ),
        }),
    )


# ─────────────────────────────────────────────
#  EVENT  (unchanged)
# ─────────────────────────────────────────────

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display  = ["title", "start_date", "city", "application_open", "published"]
    list_editable = ["published", "application_open"]
    prepopulated_fields = {"slug": ("title",)}
    list_filter  = ["published", "application_open"]
    search_fields = ["title", "city", "location"]

    fieldsets = (
        ("Core", {
            "fields": ("title", "slug", "tagline", "image", "published")
        }),
        ("Dates & Location", {
            "fields": ("start_date", "end_date", "location", "venue_name", "city")
        }),
        ("About", {
            "fields": ("description",)
        }),
        ("Schedule", {
            "fields": (
                "day1_title", "day1_schedule",
                "day2_title", "day2_schedule",
                "day3_title", "day3_schedule",
            )
        }),
        ("What Attendees Learn & Who Should Apply", {
            "fields": ("what_you_learn", "who_should_apply")
        }),
        ("FAQ", {
            "fields": ("faq",)
        }),
        ("Applications", {
            "fields": ("application_open", "application_deadline")
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        # If a non-superuser creates an Event, set them as the owner.
        if not request.user.is_superuser and not obj.owner:
            obj.owner = request.user
        super().save_model(request, obj, form, change)
