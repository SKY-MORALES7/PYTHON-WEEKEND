from django import forms
from django.contrib import admin
from django.db import models
from .models import Form, Question, Answer, OrganizerApplication, EventApplication
from content.models import Event


from django.utils.html import format_html
from django.utils.safestring import mark_safe


class EventApplicationChangelistForm(forms.ModelForm):
    class Meta:
        model = EventApplication
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.status in ("approved", "rejected"):
                if "status" in self.fields:
                    self.fields["status"].disabled = True


@admin.register(EventApplication)
class EventApplicationAdmin(admin.ModelAdmin):
    form = EventApplicationChangelistForm
    change_list_template = "admin/applications/eventapplication/change_list.html"
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

    def get_changelist_form(self, request, **kwargs):
        return EventApplicationChangelistForm

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        if obj and obj.status in ("approved", "rejected"):
            if "status" not in ro:
                ro.append("status")
        return ro

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

    @admin.action(description="Approve selected attendee applications (pending only)")
    def approve_applications(self, request, queryset):
        pending_qs = queryset.filter(status="pending")
        count = 0
        for app in pending_qs:
            app.status = "approved"
            app.save()
            count += 1
        skipped = queryset.count() - count
        if skipped > 0:
            self.message_user(
                request,
                f"{count} pending application(s) approved and notification emails sent. "
                f"{skipped} application(s) were already finalized (approved/rejected) and remained unchanged."
            )
        else:
            self.message_user(request, f"{count} application(s) approved and notification emails sent.")

    @admin.action(description="Reject selected attendee applications (pending only)")
    def reject_applications(self, request, queryset):
        pending_qs = queryset.filter(status="pending")
        count = 0
        for app in pending_qs:
            app.status = "rejected"
            app.save()
            count += 1
        skipped = queryset.count() - count
        if skipped > 0:
            self.message_user(
                request,
                f"{count} pending application(s) rejected and notification emails sent. "
                f"{skipped} application(s) were already finalized (approved/rejected) and remained unchanged."
            )
        else:
            self.message_user(request, f"{count} application(s) rejected and notification emails sent.")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "event" and not request.user.is_superuser:
            from django.db.models import Q
            kwargs["queryset"] = Event.objects.filter(
                Q(owner=request.user) | Q(co_organizers=request.user)
            ).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_field_queryset(self, db, db_field, request):
        if db_field.name == "event" and not request.user.is_superuser:
            from django.db.models import Q
            return Event.objects.filter(
                Q(owner=request.user) | Q(co_organizers=request.user)
            ).distinct()
        return super().get_field_queryset(db, db_field, request)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        from django.db.models import Q
        return qs.filter(Q(event__owner=request.user) | Q(event__co_organizers=request.user)).distinct()

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        from django.db.models import Q

        base_qs = self.get_queryset(request)

        # Single event drilled down mode
        event_id = request.GET.get("event__id__exact") or request.GET.get("event__id")
        current_event = None
        if event_id:
            try:
                current_event = Event.objects.get(pk=int(event_id))
            except (Event.DoesNotExist, ValueError):
                pass

        extra_context["current_event"] = current_event

        if current_event:
            ev_apps = base_qs.filter(event=current_event)
            extra_context["current_event_total"] = ev_apps.count()
            extra_context["current_event_approved"] = ev_apps.filter(status="approved").count()
            extra_context["current_event_pending"] = ev_apps.filter(status="pending").count()
            extra_context["current_event_rejected"] = ev_apps.filter(status="rejected").count()
            extra_context["is_grouped_view"] = False
        else:
            # Grouped view overview for all accessible events
            if request.user.is_superuser:
                accessible_events = Event.objects.all().order_by("-start_date", "-id")
            else:
                accessible_events = Event.objects.filter(
                    Q(owner=request.user) | Q(co_organizers=request.user)
                ).distinct().order_by("-start_date", "-id")

            grouped_data = []
            for ev in accessible_events:
                ev_apps = base_qs.filter(event=ev)
                tot = ev_apps.count()
                appr = ev_apps.filter(status="approved").count()
                pend = ev_apps.filter(status="pending").count()
                rej = ev_apps.filter(status="rejected").count()
                expected = getattr(ev, "expected_attendees", 50) or 50
                pct = min(100, int((tot / expected) * 100)) if expected > 0 else 0

                grouped_data.append({
                    "event": ev,
                    "expected_attendees": expected,
                    "total_applicants": tot,
                    "approved_count": appr,
                    "pending_count": pend,
                    "rejected_count": rej,
                    "progress_pct": pct,
                    "applications": list(ev_apps[:10]),
                    "has_more": tot > 10,
                })

            unassigned_apps = base_qs.filter(event__isnull=True)
            if unassigned_apps.exists():
                u_tot = unassigned_apps.count()
                grouped_data.append({
                    "event": None,
                    "expected_attendees": "N/A",
                    "total_applicants": u_tot,
                    "approved_count": unassigned_apps.filter(status="approved").count(),
                    "pending_count": unassigned_apps.filter(status="pending").count(),
                    "rejected_count": unassigned_apps.filter(status="rejected").count(),
                    "progress_pct": 0,
                    "applications": list(unassigned_apps[:10]),
                    "has_more": u_tot > 10,
                })

            extra_context["grouped_events"] = grouped_data
            extra_context["is_grouped_view"] = bool(request.GET.get("view") != "flat" and not request.GET.get("q"))

        return super().changelist_view(request, extra_context=extra_context)


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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "event" and not request.user.is_superuser:
            from django.db.models import Q
            from content.models import Event
            kwargs["queryset"] = Event.objects.filter(
                Q(owner=request.user) | Q(co_organizers=request.user)
            ).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "form" and not request.user.is_superuser:
            from django.db.models import Q
            from applications.models import Form
            kwargs["queryset"] = Form.objects.filter(
                Q(event__owner=request.user) | Q(event__co_organizers=request.user)
            ).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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
        "expected_attendees",
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
        ("Workshop Details & Capacity", {
            "fields": ("workshop_type", "expected_attendees", "prerequisites_confirmed", "commitment_signed")
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


