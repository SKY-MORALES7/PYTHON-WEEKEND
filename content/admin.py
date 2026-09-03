from django.contrib import admin
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from .models import (
    BlogPost, BlogSection, Event,
    WebsiteContent, WebsiteMenus,
    EventCoach, EventSponsor,
    PageContent, WebsiteMenuItem, FooterConfig,
)


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
#  EVENT INLINES
# ─────────────────────────────────────────────

class EventCoachInline(admin.TabularInline):
    model = EventCoach
    extra = 1
    autocomplete_fields = ["coach"]
    fields = ("coach", "role", "order")
    ordering = ("order",)
    verbose_name = "Coach"
    verbose_name_plural = "Coaches"


class EventSponsorInline(admin.TabularInline):
    model = EventSponsor
    extra = 1
    autocomplete_fields = ["sponsor"]
    fields = ("sponsor", "description", "order")
    ordering = ("order",)
    verbose_name = "Sponsor"
    verbose_name_plural = "Sponsors"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display  = ["title", "start_date", "city", "country", "application_open", "published"]
    list_editable = ["published", "application_open"]
    prepopulated_fields = {"slug": ("title",)}
    list_filter  = ["published", "application_open", "country"]
    search_fields = ["title", "city", "location", "country"]
    inlines = [EventCoachInline, EventSponsorInline]

    fieldsets = (
        ("Core", {
            "fields": ("title", "slug", "tagline", "image", "published")
        }),
        ("Dates & Location", {
            "fields": ("start_date", "end_date", "location", "venue_name", "city", "country")
        }),
        ("Map Coordinates", {
            "fields": ("latitude", "longitude"),
            "classes": ("collapse",),
            "description": "Optional — used on the event map page."
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
        ("Impact", {
            "fields": ("attendees_count",),
            "description": "Update after the event with verified attendance numbers."
        }),
        ("Customization", {
            "fields": ("custom_html", "custom_css", "sponsors_title", "schedule_title")
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


# ─────────────────────────────────────────────
#  PAGE CONTENT
# ─────────────────────────────────────────────

@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display  = ["label", "page_badge", "content_type_badge", "value_preview", "updated_at"]
    list_filter   = ["page", "content_type"]
    search_fields = ["key", "label", "value"]
    readonly_fields = ["key", "label", "content_type", "page", "hint_display"]
    ordering      = ["page", "key"]

    fieldsets = (
        (None, {
            "fields": ("page", "label", "key", "content_type"),
            "description": (
                "<strong>Note:</strong> The Page, Label, Key, and Content Type fields are "
                "set automatically and cannot be changed here. Only edit the <em>Value</em> field below."
            ),
        }),
        ("✏️ Edit Content", {
            "fields": ("hint_display", "value"),
        }),
    )

    def hint_display(self, obj):
        """Shows the admin_help_text as a styled hint box in the edit form."""
        if obj.admin_help_text:
            return format_html(
                '<div style="background:#fffbec;border-left:4px solid #f0ad00;'
                'padding:0.75rem 1rem;border-radius:0 0.375rem 0.375rem 0;'
                'font-size:0.9rem;color:#4a4a4a;max-width:700px;">'
                '💡 <strong>Guidance:</strong> {}'
                '</div>',
                obj.admin_help_text,
            )
        return "—"
    hint_display.short_description = "What to write"

    def page_badge(self, obj):
        colours = {
            "home": "#4B8BBE", "about": "#306998", "contact": "#FFD43B",
            "support": "#28a745", "faq": "#6f42c1", "coc": "#fd7e14",
            "organise": "#20c997", "contribute": "#e83e8c",
            "resources": "#17a2b8", "newsletter": "#6c757d",
            "jobs": "#dc3545", "global": "#343a40",
        }
        colour = colours.get(obj.page, "#6c757d")
        text_colour = "#fff" if obj.page != "contact" else "#333"
        return format_html(
            '<span style="background:{};color:{};padding:2px 8px;'
            'border-radius:12px;font-size:0.78rem;font-weight:600;">{}</span>',
            colour, text_colour, obj.get_page_display(),
        )
    page_badge.short_description = "Page"

    def content_type_badge(self, obj):
        colour = "#4B8BBE" if obj.content_type == "text" else "#306998"
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:12px;font-size:0.78rem;">{}</span>',
            colour, obj.get_content_type_display(),
        )
    content_type_badge.short_description = "Type"

    def value_preview(self, obj):
        if obj.value:
            preview = obj.value[:80] + ("…" if len(obj.value) > 80 else "")
            return format_html('<span style="color:#333;">{}</span>', preview)
        return format_html('<span style="color:#aaa;font-style:italic;">Not set — using template default</span>')
    value_preview.short_description = "Current Value"

    def has_add_permission(self, request):
        # Content rows are created only by data migrations, not manually.
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # Prevent accidental deletion — rows are managed by migrations.
        return request.user.is_superuser

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Bust the content cache so the website reflects changes immediately.
        from django.core.cache import cache
        cache.delete("site_page_content_map")


# ─────────────────────────────────────────────
#  WEBSITE MENU ITEMS
# ─────────────────────────────────────────────

class ChildMenuItemInline(admin.TabularInline):
    model = WebsiteMenuItem
    fk_name = "parent"
    extra = 1
    fields = ("label", "url", "order", "open_in_new_tab", "is_active")
    ordering = ("order",)
    verbose_name = "Dropdown Child"
    verbose_name_plural = "Dropdown Children"

    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(WebsiteMenuItem)
class WebsiteMenuItemAdmin(admin.ModelAdmin):
    list_display  = [
        "indented_label", "position_badge", "url", "footer_column",
        "order", "is_active", "open_in_new_tab",
    ]
    list_editable = ["order", "is_active", "open_in_new_tab"]
    list_filter   = ["position", "is_active", "footer_column"]
    search_fields = ["label", "url", "footer_column"]
    ordering      = ["position", "order", "label"]
    inlines       = [ChildMenuItemInline]

    fieldsets = (
        ("Link", {
            "fields": ("label", "url", "open_in_new_tab"),
        }),
        ("Position", {
            "fields": ("position", "parent"),
            "description": (
                "For <strong>header</strong> items: set Parent to make this a dropdown child. "
                "Leave Parent blank for top-level items (those with dropdowns).<br>"
                "For <strong>footer</strong> items: leave Parent blank and set Footer Column "
                "to group this link into a column."
            ),
        }),
        ("Footer Column", {
            "fields": ("footer_column",),
            "classes": ("collapse",),
            "description": "Footer items only. Type the column heading this link belongs to.",
        }),
        ("Display", {
            "fields": ("order", "is_active"),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("parent")

    def indented_label(self, obj):
        if obj.parent_id:
            return format_html(
                '<span style="margin-left:1.5rem;color:#6c757d;">↳ {}</span>',
                obj.label,
            )
        return format_html('<strong>{}</strong>', obj.label)
    indented_label.short_description = "Label"

    def position_badge(self, obj):
        colour = "#4B8BBE" if obj.position == "header" else "#16213E"
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:12px;font-size:0.78rem;font-weight:600;">{}</span>',
            colour, obj.get_position_display(),
        )
    position_badge.short_description = "Position"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        from django.core.cache import cache
        cache.delete(f"site_menu_{obj.position}")
        cache.delete(f"site_menu_header")
        cache.delete(f"site_menu_footer")

    def delete_model(self, request, obj):
        position = obj.position
        super().delete_model(request, obj)
        from django.core.cache import cache
        cache.delete(f"site_menu_{position}")


# ─────────────────────────────────────────────
#  FOOTER CONFIG  (singleton)
# ─────────────────────────────────────────────

@admin.register(FooterConfig)
class FooterConfigAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Brand", {
            "fields": ("tagline", "copyright_text"),
        }),
        ("Social Media Links", {
            "fields": ("facebook_url", "instagram_url", "twitter_url", "linkedin_url"),
            "description": "Leave blank to hide a social icon.",
        }),
    )

    def has_add_permission(self, request):
        # Only one FooterConfig row should ever exist.
        return not FooterConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        """Redirect the list view straight to the single config object's edit page."""
        cfg, _ = FooterConfig.objects.get_or_create(pk=1)
        return HttpResponseRedirect(
            reverse("admin:content_footerconfig_change", args=[cfg.pk])
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        from django.core.cache import cache
        cache.delete("site_footer_config")


# ─────────────────────────────────────────────
#  LEGACY MODELS (hidden from admin by default)
# ─────────────────────────────────────────────

@admin.register(WebsiteContent)
class WebsiteContentAdmin(admin.ModelAdmin):
    list_display = ["title", "location_identifier", "updated_at"]
    search_fields = ["title", "location_identifier"]

    def get_model_perms(self, request):
        """Hide from main admin index — legacy model."""
        return {} if not request.user.is_superuser else super().get_model_perms(request)


@admin.register(WebsiteMenus)
class WebsiteMenusAdmin(admin.ModelAdmin):
    list_display = ["name", "position", "order", "is_active"]
    list_filter = ["position", "is_active"]
    list_editable = ["order", "is_active"]
    search_fields = ["name", "url"]

    def get_model_perms(self, request):
        """Hide from main admin index — legacy model."""
        return {} if not request.user.is_superuser else super().get_model_perms(request)
