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

    def has_add_permission(self, request):
        # Event applications must always originate from frontend attendee submissions
        return False

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

            # Organizer lookup for drilled-down event
            cur_org_app = None
            if current_event.owner and current_event.owner.email:
                cur_org_app = OrganizerApplication.objects.filter(lead_email__iexact=current_event.owner.email).order_by("-submitted_at").first()
            if not cur_org_app and hasattr(current_event, 'returning_organizers'):
                cur_org_app = current_event.returning_organizers.order_by("-submitted_at").first()
            if cur_org_app:
                extra_context["current_event_organizer_name"] = f"{cur_org_app.lead_first_name} {cur_org_app.lead_last_name}".strip()
                extra_context["current_event_organizer_app_id"] = cur_org_app.id
            elif current_event.owner:
                extra_context["current_event_organizer_name"] = f"{current_event.owner.first_name} {current_event.owner.last_name}".strip() or current_event.owner.username
                extra_context["current_event_organizer_app_id"] = None
            else:
                extra_context["current_event_organizer_name"] = "Platform Admin"
                extra_context["current_event_organizer_app_id"] = None
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

                # Organizer lookup for admin view
                organizer_name = None
                organizer_app_id = None
                org_app = None

                if ev.owner:
                    if ev.owner.email:
                        org_app = OrganizerApplication.objects.filter(lead_email__iexact=ev.owner.email).order_by("-submitted_at").first()
                    if not org_app and (ev.owner.first_name or ev.owner.last_name):
                        org_app = OrganizerApplication.objects.filter(
                            Q(lead_first_name__iexact=ev.owner.first_name, lead_last_name__iexact=ev.owner.last_name) |
                            Q(lead_first_name__iexact=ev.owner.first_name)
                        ).order_by("-submitted_at").first()

                if not org_app and hasattr(ev, 'returning_organizers'):
                    org_app = ev.returning_organizers.order_by("-submitted_at").first()

                if not org_app and ev.co_organizers.exists():
                    co_emails = list(ev.co_organizers.values_list('email', flat=True))
                    org_app = OrganizerApplication.objects.filter(lead_email__in=co_emails).order_by("-submitted_at").first()

                if not org_app:
                    # Match by target state or country in event title or city
                    for cand in OrganizerApplication.objects.all():
                        if cand.target_state and (cand.target_state.lower() in ev.title.lower() or (ev.city and cand.target_state.lower() in ev.city.lower())):
                            org_app = cand
                            break

                if org_app:
                    organizer_name = f"{org_app.lead_first_name} {org_app.lead_last_name}".strip()
                    organizer_app_id = org_app.id
                elif ev.owner:
                    organizer_name = f"{ev.owner.first_name} {ev.owner.last_name}".strip() or ev.owner.username
                else:
                    organizer_name = "Platform Admin"

                grouped_data.append({
                    "event": ev,
                    "expected_attendees": expected,
                    "total_applicants": tot,
                    "approved_count": appr,
                    "pending_count": pend,
                    "rejected_count": rej,
                    "progress_pct": pct,
                    "applications": list(ev_apps[:2]),
                    "has_more": tot > 2,
                    "organizer_name": organizer_name,
                    "organizer_app_id": organizer_app_id,
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
                    "applications": list(unassigned_apps[:2]),
                    "has_more": u_tot > 2,
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
    readonly_fields = ("team_members_display", "submitted_at", "updated_at")

    fieldsets = (
        ("Lead Organizer", {
            "fields": ("lead_first_name", "lead_last_name", "lead_email")
        }),
        ("Team Members", {
            "fields": ("team_members_display",),
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

    @admin.display(description="Team Members")
    def team_members_display(self, obj):
        from django.utils.html import escape
        members = obj.team_members
        if not members or not isinstance(members, list):
            return format_html('<span style="color: #64748b; font-style: italic;">No additional team members provided.</span>')

        rows = []
        for idx, m in enumerate(members, 1):
            if isinstance(m, dict):
                first = escape(str(m.get("first_name", ""))).strip()
                last = escape(str(m.get("last_name", ""))).strip()
                email = escape(str(m.get("email", ""))).strip()
                full_name = f"{first} {last}".strip() or "Unnamed"
                email_link = f'<a href="mailto:{email}" style="color: #0284c7; text-decoration: underline; font-weight: 600;">{email}</a>' if email else '—'
                rows.append(
                    f'<tr style="border-bottom: 1.5px solid #e2e8f0; background: #ffffff;">'
                    f'<td style="padding: 10px 16px; font-weight: 800; color: #16213E; font-family: monospace;">#{idx}</td>'
                    f'<td style="padding: 10px 16px; font-weight: 700; color: #16213E;">{full_name}</td>'
                    f'<td style="padding: 10px 16px;">{email_link}</td>'
                    f'</tr>'
                )

        if not rows:
            return format_html('<span style="color: #64748b; font-style: italic;">No additional team members provided.</span>')

        html = (
            f'<div style="max-width: 650px; background: #ffffff; border: 2px solid #16213E; box-shadow: 3px 3px 0 #16213E; margin-top: 4px;">'
            f'<table style="width: 100%; border-collapse: collapse; font-size: 13px;">'
            f'<thead>'
            f'<tr style="background: #16213E; color: #ffffff; text-transform: uppercase; font-size: 11px; letter-spacing: 0.05em;">'
            f'<th style="padding: 10px 16px; text-align: left; width: 45px;">#</th>'
            f'<th style="padding: 10px 16px; text-align: left;">Full Name</th>'
            f'<th style="padding: 10px 16px; text-align: left;">Email Address</th>'
            f'</tr>'
            f'</thead>'
            f'<tbody>'
            f'{"".join(rows)}'
            f'</tbody>'
            f'</table>'
            f'</div>'
        )
        return mark_safe(html)

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

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


