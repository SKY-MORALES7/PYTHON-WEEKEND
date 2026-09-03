from django.contrib import admin
from django.db import models
from .models import Form, Question, Answer, OrganizerApplication, EventApplication


@admin.register(EventApplication)
class EventApplicationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "city", "country", "expected_attendees", "status")
    list_filter = ("status", "country")
    list_editable = ("status",)
    search_fields = ("full_name", "email", "city")



# ─────────────────────────────────────────────
#  QUESTION INLINE (inside Form)
# ─────────────────────────────────────────────

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    verbose_name_plural = "Questions (Note: 'Full Name' and 'Email Address' are automatically added to new forms)"
    fields = ("order", "title", "question_type", "choices", "is_required")
    ordering = ("order",)
    formfield_overrides = {
        models.TextField: {'widget': admin.widgets.AdminTextareaWidget(attrs={'rows': 3, 'cols': 60})},
        models.CharField: {'widget': admin.widgets.AdminTextInputWidget(attrs={'size': 60})},
    }
    class Media:
        js = ("js/admin_question_inline.js",)


# ─────────────────────────────────────────────
#  FORM
# ─────────────────────────────────────────────

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ("event", "text_header", "is_open", "created_at")
    list_filter = ("is_open",)
    search_fields = ("event__title", "text_header")
    inlines = [QuestionInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(event__owner=request.user)


# ─────────────────────────────────────────────
#  QUESTION
# ─────────────────────────────────────────────

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "form", "question_type", "is_required", "order")
    list_filter = ("question_type", "is_required")
    search_fields = ("title",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(form__event__owner=request.user)


# ─────────────────────────────────────────────
#  ANSWER
# ─────────────────────────────────────────────

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "applicant_email", "submitted_at")
    list_filter = ("submitted_at",)
    search_fields = ("applicant_email", "answer")
    readonly_fields = ("submitted_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(question__form__event__owner=request.user)


# ─────────────────────────────────────────────
#  ORGANIZER APPLICATION
# ─────────────────────────────────────────────

@admin.register(OrganizerApplication)
class OrganizerApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "lead_first_name",
        "lead_last_name",
        "lead_email",
        "workshop_type",
        "has_organized_before",
        "status",
        "submitted_at",
    )
    list_filter = ("status", "workshop_type", "has_organized_before")
    list_editable = ("status",)
    search_fields = ("lead_first_name", "lead_last_name", "lead_email")
    readonly_fields = ("submitted_at", "updated_at")

    fieldsets = (
        ("Lead Organizer", {
            "fields": ("lead_first_name", "lead_last_name", "lead_email")
        }),
        ("Team Members", {
            "fields": ("team_members",),
        }),
        ("Workshop Details", {
            "fields": ("workshop_type", "prerequisites_confirmed", "commitment_signed")
        }),
        ("Experience", {
            "fields": ("has_organized_before", "previous_event")
        }),
        ("Status", {
            "fields": ("status", "submitted_at", "updated_at")
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.none()


