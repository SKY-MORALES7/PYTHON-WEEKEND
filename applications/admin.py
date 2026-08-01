from django.contrib import admin
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

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ("order", "title", "question_type", "is_required")
    ordering = ("order",)


# ─────────────────────────────────────────────
#  FORM
# ─────────────────────────────────────────────

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ("event", "text_header", "is_open", "created_at")
    list_filter = ("is_open",)
    search_fields = ("event__title", "text_header")
    inlines = [QuestionInline]


# ─────────────────────────────────────────────
#  QUESTION
# ─────────────────────────────────────────────

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "form", "question_type", "is_required", "order")
    list_filter = ("question_type", "is_required")
    search_fields = ("title",)


# ─────────────────────────────────────────────
#  ANSWER
# ─────────────────────────────────────────────

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "applicant_email", "submitted_at")
    list_filter = ("submitted_at",)
    search_fields = ("applicant_email", "answer")
    readonly_fields = ("submitted_at",)


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

    def save_model(self, request, obj, form, change):
        if change:
            # Fetch the old object from DB to compare status
            old_obj = OrganizerApplication.objects.get(pk=obj.pk)
            if old_obj.status != obj.status:
                if obj.status == "approved":
                    self.handle_approval(obj)
                elif obj.status == "rejected":
                    self.handle_rejection(obj)
        super().save_model(request, obj, form, change)

    def _get_all_applicants(self, obj):
        people = [
            {
                "first_name": obj.lead_first_name,
                "last_name": obj.lead_last_name,
                "email": obj.lead_email
            }
        ]
        if isinstance(obj.team_members, list):
            for member in obj.team_members:
                if member.get("email") and member.get("first_name"):
                    people.append({
                        "first_name": member.get("first_name", ""),
                        "last_name": member.get("last_name", ""),
                        "email": member.get("email", "")
                    })
        return people

    def handle_approval(self, obj):
        from django.contrib.auth import get_user_model
        from django.core.mail import send_mass_mail
        from django.conf import settings

        User = get_user_model()
        people = self._get_all_applicants(obj)
        messages = []

        for person in people:
            email = person["email"].strip()
            first_name = person["first_name"].strip()
            last_name = person["last_name"].strip()

            user = User.objects.filter(email=email).first()
            if not user:
                base = first_name.lower().replace(" ", "") or "user"
                num = 1
                while True:
                    username = f"{base}{num}"
                    if not User.objects.filter(username=username).exists():
                        break
                    num += 1

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password="admin123",
                    first_name=first_name,
                    last_name=last_name
                )
                
                # We can also make them staff if they are an organizer, but we'll stick to simple user for now.
                # If they need admin access to edit events:
                user.is_staff = True
                user.save()

            subject = "Your Python Weekend Organizer Application has been Approved!"
            body = (
                f"Hi {first_name},\n\n"
                f"Congratulations! Your application to organize a Python Weekend has been approved.\n"
                f"You have been granted access to the platform.\n\n"
                f"Your Login Details:\n"
                f"Username: {user.username}\n"
                f"Password: admin123\n\n"
                f"Please log in and you can change your password from the admin panel.\n\n"
                f"Best,\nThe Python Weekend Team"
            )
            messages.append((subject, body, settings.DEFAULT_FROM_EMAIL, [email]))

        if messages:
            send_mass_mail(messages, fail_silently=True)

    def handle_rejection(self, obj):
        from django.core.mail import send_mass_mail
        from django.conf import settings

        people = self._get_all_applicants(obj)
        messages = []

        for person in people:
            email = person["email"].strip()
            first_name = person["first_name"].strip()
            
            subject = "Python Weekend Organizer Application Update"
            body = (
                f"Hi {first_name},\n\n"
                f"Thank you for your interest in organizing a Python Weekend.\n"
                f"Unfortunately, your application has not been approved at this time.\n\n"
                f"Best,\nThe Python Weekend Team"
            )
            messages.append((subject, body, settings.DEFAULT_FROM_EMAIL, [email]))

        if messages:
            send_mass_mail(messages, fail_silently=True)