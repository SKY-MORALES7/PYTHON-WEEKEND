from django.contrib import admin
from django.db import models
from .models import Form, Question, Answer, OrganizerApplication, EventApplication


from django.utils.html import format_html
from django.utils.safestring import mark_safe

@admin.register(EventApplication)
class EventApplicationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "event", "status", "created_at")
    list_filter = ("status", "event", "created_at")
    list_editable = ("status",)
    search_fields = ("full_name", "email", "event__title")
    readonly_fields = ("created_at", "submitted_answers_display")

    fieldsets = (
        ("Applicant Information", {
            "fields": ("full_name", "email", "event", "created_at"),
        }),
        ("Submitted Questions & Answers", {
            "fields": ("submitted_answers_display",),
            "description": "The exact questions and responses provided by the applicant when filling out this event's application form.",
        }),
        ("Review & Approval", {
            "fields": ("status",),
        }),
    )

    @admin.display(description="Submitted Responses")
    def submitted_answers_display(self, obj):
        if not obj.pk:
            return "Save this application to view responses."

        # Fetch answers linked directly to this application, or fallback to email/form match
        answers = list(obj.answers.select_related("question").all())
        if not answers and obj.form:
            answers = list(Answer.objects.filter(question__form=obj.form, applicant_email=obj.email).select_related("question"))

        if not answers:
            return format_html("<p style='color: #64748b; font-style: italic;'>No answers recorded for this applicant.</p>")

        html_blocks = ["<div style='display: flex; flex-direction: column; gap: 0.85rem; max-width: 760px; margin-top: 0.5rem;'>"]
        for ans in answers:
            q_title = ans.question.title
            q_val = ans.answer.strip() if ans.answer else "(No answer provided)"
            html_blocks.append(
                format_html(
                    """
                    <div style="background: #f8fafc; border: 1.5px solid #cbd5e1; border-left: 4px solid #306998; padding: 0.85rem 1.15rem; border-radius: 4px;">
                        <div style="font-weight: 700; color: #16213e; font-size: 0.95rem; margin-bottom: 0.35rem;">{}</div>
                        <div style="color: #334155; font-size: 0.95rem; white-space: pre-wrap; line-height: 1.55;">{}</div>
                    </div>
                    """,
                    q_title,
                    q_val
                )
            )
        html_blocks.append("</div>")
        return mark_safe("".join(html_blocks))

    actions = ["approve_applications", "reject_applications"]

    @admin.action(description="Approve selected attendee applications")
    def approve_applications(self, request, queryset):
        count = 0
        for app in queryset:
            if app.status != "approved":
                app.status = "approved"
                app.save()
                count += 1
        self.message_user(request, f"{count} application(s) approved and notification emails sent.")

    @admin.action(description="Reject selected attendee applications")
    def reject_applications(self, request, queryset):
        count = 0
        for app in queryset:
            if app.status != "rejected":
                app.status = "rejected"
                app.save()
                count += 1
        self.message_user(request, f"{count} application(s) rejected and notification emails sent.")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        from django.db.models import Q
        return qs.filter(Q(event__owner=request.user) | Q(event__co_organizers=request.user)).distinct()





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
        from django.db.models import Q
        return qs.filter(Q(event__owner=request.user) | Q(event__co_organizers=request.user)).distinct()


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
        from django.db.models import Q
        return qs.filter(Q(form__event__owner=request.user) | Q(form__event__co_organizers=request.user)).distinct()


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
        from django.db.models import Q
        return qs.filter(Q(question__form__event__owner=request.user) | Q(question__form__event__co_organizers=request.user)).distinct()


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
        "previous_event",
        "target_country",
        "target_state",
        "status",
        "submitted_at",
    )
    list_filter = ("status", "workshop_type", "has_organized_before", "target_country")
    list_editable = ("status",)
    search_fields = ("lead_first_name", "lead_last_name", "lead_email", "target_country", "target_state")
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
        ("Experience & Target Location", {
            "fields": ("has_organized_before", "previous_event", "target_country", "target_state")
        }),
        ("Status", {
            "fields": ("status", "submitted_at", "updated_at")
        }),
    )

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.none()


