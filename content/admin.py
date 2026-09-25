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


from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone


class EventAdminForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        application_open = cleaned_data.get("application_open")

        if start_date and end_date and end_date < start_date:
            raise ValidationError({"end_date": "End date cannot be earlier than start date."})

        if application_open and start_date and start_date < timezone.now():
            raise ValidationError({"application_open": "The start date has already passed. Applications cannot be open for a past event."})

        return cleaned_data


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
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
            "fields": ("custom_html", "sponsors_title", "schedule_title")
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not obj.owner:
            obj.owner = request.user
        super().save_model(request, obj, form, change)


# ─────────────────────────────────────────────
#  WEBSITE CONTENT — per-page admin base class
# ─────────────────────────────────────────────

class PageContentAdmin(admin.ModelAdmin):
    """
    Admin for website content.
    If no 'page' filter is active, it renders a custom template showing buttons for each page.
    If a 'page' filter is active, it shows the list of fields for that page.
    """
    list_display  = ["label", "value_preview", "content_type_badge", "updated_at"]
    search_fields = ["label", "value"]
    ordering      = ["key"]
    readonly_fields = ["key", "label", "content_type", "hint_display"]
    list_filter   = ["page"]

    fieldsets = (
        (None, {
            "fields": ("label", "key", "content_type"),
            "description": (
                "<strong>Note:</strong> Label, Key, and Type are set automatically. "
                "Only edit the <em>Value</em> field below."
            ),
        }),
        ("✏️ Edit Content", {
            "fields": ("hint_display", "value"),
        }),
    )

    def changelist_view(self, request, extra_context=None):
        if not request.GET.get('page__exact'):
            # Show the category grid if no page is selected
            from django.template.response import TemplateResponse
            from .models import PageContent
            pages = []
            for slug, name in PageContent.PAGE_CHOICES:
                pages.append({"slug": slug, "name": name})
            
            context = {
                **self.admin_site.each_context(request),
                "title": "Select a Website Page to Edit",
                "pages": pages,
                "opts": self.model._meta,
            }
            return TemplateResponse(request, "admin/content/pagecontent/page_grid.html", context)
        
        return super().changelist_view(request, extra_context)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        from django.core.cache import cache
        cache.delete("site_page_content_map")

    # ── Display helpers ──────────────────────────────────────────────────────

    def hint_display(self, obj):
        if obj.admin_help_text:
            return format_html(
                '<div style="background:#fffbec;border-left:4px solid #f0ad00;'
                'padding:0.75rem 1rem;border-radius:0 0.375rem 0.375rem 0;'
                'font-size:0.9rem;color:#4a4a4a;max-width:700px;">'
                '💡 <strong>What to write:</strong> {}'
                '</div>',
                obj.admin_help_text,
            )
        return "—"
    hint_display.short_description = "Guidance"

    def value_preview(self, obj):
        if obj.value:
            preview = obj.value[:90] + ("…" if len(obj.value) > 90 else "")
            return format_html('<span style="color:#333;">{}</span>', preview)
        return format_html(
            '<span style="color:#bbb;font-style:italic;">Not set — template default will show</span>'
        )
    value_preview.short_description = "Current Value (click to edit)"

    def content_type_badge(self, obj):
        colour = "#4B8BBE" if obj.content_type == "text" else "#306998"
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:12px;font-size:0.78rem;">{}</span>',
            colour, obj.get_content_type_display(),
        )
    content_type_badge.short_description = "Type"

admin.site.register(PageContent, PageContentAdmin)



# ─────────────────────────────────────────────
#  WEBSITE MENUS
#  Single admin entry — shows ALL header + footer items together
# ─────────────────────────────────────────────

class ChildMenuItemInline(admin.TabularInline):
    model = WebsiteMenuItem
    fk_name = "parent"
    extra = 1
    fields = ("label", "url", "order", "open_in_new_tab", "is_active")
    ordering = ("order",)
    verbose_name = "Dropdown child link"
    verbose_name_plural = "Dropdown child links (shown under this item)"

    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(WebsiteMenuItem)
class WebsiteMenuItemAdmin(admin.ModelAdmin):
    list_display  = [
        "indented_label", "position_badge", "url",
        "footer_column", "order", "is_active",
    ]
    list_editable = ["order", "is_active"]
    list_filter   = ["position", "is_active"]
    search_fields = ["label", "url", "footer_column"]
    ordering      = ["position", "order", "label"]
    inlines       = [ChildMenuItemInline]

    fieldsets = (
        ("Link details", {
            "fields": ("label", "url", "open_in_new_tab"),
            "description": (
                "Set the text shown in the navigation and the URL it links to."
            ),
        }),
        ("Where does this appear?", {
            "fields": ("position", "parent"),
            "description": (
                "<strong>Header items:</strong> leave Parent blank for top-level links "
                "(they appear in the main nav bar). Set Parent to make this a dropdown child "
                "under another header item.<br>"
                "<strong>Footer items:</strong> leave Parent blank. Set Footer Column "
                "to group this link into a labelled column."
            ),
        }),
        ("Footer column (footer items only)", {
            "fields": ("footer_column",),
            "description": (
                "Type the column heading this footer link belongs to, "
                "e.g. <em>Python Weekend</em>, <em>Support Us</em>, <em>Resources</em>, <em>Legal</em>."
            ),
        }),
        ("Display order", {
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
    indented_label.admin_order_field = "label"

    def position_badge(self, obj):
        colour = "#4B8BBE" if obj.position == "header" else "#16213E"
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;'
            'border-radius:12px;font-size:0.78rem;font-weight:600;">{}</span>',
            colour, obj.get_position_display(),
        )
    position_badge.short_description = "Position"
    position_badge.admin_order_field = "position"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        from .models import FooterConfig
        cfg, _ = FooterConfig.objects.get_or_create(pk=1)
        extra_context['footer_config_url'] = reverse("admin:content_footerconfig_change", args=[cfg.pk])
        return super().changelist_view(request, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        from django.core.cache import cache
        cache.delete("site_menu_header")
        cache.delete("site_menu_footer")

    def delete_model(self, request, obj):
        position = obj.position
        super().delete_model(request, obj)
        from django.core.cache import cache
        cache.delete(f"site_menu_{position}")


# ─────────────────────────────────────────────
#  FOOTER CONFIG  (social links, tagline, copyright)
# ─────────────────────────────────────────────

@admin.register(FooterConfig)
class FooterConfigAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Brand Tagline & Copyright", {
            "fields": ("tagline", "copyright_text"),
            "description": (
                "The copyright text appears as a single line at the bottom of every page. "
                "Use {year} as a dynamic year placeholder. "
                "In the template's static fallback, \"Code Campus\" is automatically rendered as a link to codecampus.com.ng."
            ),
        }),
        ("Social Media Links", {
            "fields": ("facebook_url", "instagram_url", "twitter_url", "linkedin_url"),
            "description": "Leave any field blank to hide that social icon in the footer.",
        }),
    )

    def get_model_perms(self, request):
        return {}  # Hide from admin index (accessed via WebsiteMenuItemAdmin)

    def has_add_permission(self, request):
        return not FooterConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        cfg, _ = FooterConfig.objects.get_or_create(pk=1)
        return HttpResponseRedirect(
            reverse("admin:content_footerconfig_change", args=[cfg.pk])
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        from django.core.cache import cache
        cache.delete("site_footer_config")


# ─────────────────────────────────────────────
#  LEGACY MODELS — hidden from sidebar
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
#  LEGACY STUBS
#  (These models are kept to avoid migration conflicts, but are intentionally hidden from the admin)
# ─────────────────────────────────────────────
