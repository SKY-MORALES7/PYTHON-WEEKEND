import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from .models import Form, OrganizerApplication
from .forms import DynamicApplicationForm
from content.models import Event



# ─────────────────────────────────────────────
#  DYNAMIC APPLICATION FORM VIEW (existing)
# ─────────────────────────────────────────────

class ApplicationFormView(View):
    """Displays and processes a dynamic application form for an event."""
    template_name = "applications/event_application.html"

    def get(self, request, form_id):
        application_form = get_object_or_404(Form, pk=form_id, is_open=True)
        form = DynamicApplicationForm(application_form=application_form)
        return render(request, self.template_name, {
            "form": form,
            "application_form": application_form,
        })

    def post(self, request, form_id):
        application_form = get_object_or_404(Form, pk=form_id, is_open=True)
        form = DynamicApplicationForm(request.POST, application_form=application_form)

        if form.is_valid():
            applicant_email = ""
            for question in application_form.questions.all():
                if question.question_type == "email":
                    field_name = f"question_{question.pk}"
                    applicant_email = form.cleaned_data.get(field_name, "")
                    break

            form.save_answers(applicant_email=applicant_email or "unknown@example.com")
            from django.contrib import messages
            messages.success(request, "Application submitted — we'll review and be in touch.")
            return redirect("applications:apply", form_id=form_id)

        from django.contrib import messages
        messages.error(request, "There were errors with your submission. Please correct the fields below.")
        return render(request, self.template_name, {
            "form": form,
            "application_form": application_form,
        })


# ─────────────────────────────────────────────
#  ORGANIZER APPLICATION WIZARD  (5-step)
# ─────────────────────────────────────────────

WIZARD_TEMPLATES = {
    1: "applications/organize/step1_organizer.html",
    2: "applications/organize/step2_prerequisites.html",
    3: "applications/organize/step3_workshop_type.html",
    4: "applications/organize/step4_commitment.html",
    5: "applications/organize/step5_experience.html",
}

WIZARD_TOTAL_STEPS = 5


class OrganizeWizardView(View):
    """Multi-step wizard for organizer applications."""

    def get(self, request, step=1):
        step = max(1, min(step, WIZARD_TOTAL_STEPS))
        template = WIZARD_TEMPLATES[step]
        context = self._build_context(request, step)
        return render(request, template, context)

    def post(self, request, step=1):
        step = max(1, min(step, WIZARD_TOTAL_STEPS))
        wizard_data = request.session.get("organize_wizard", {})

        if step == 1:
            errors = {}
            first_name = request.POST.get("lead_first_name", "").strip()
            last_name = request.POST.get("lead_last_name", "").strip()
            email = request.POST.get("lead_email", "").strip()

            if not first_name:
                errors["lead_first_name"] = "First name is required."
            if not email:
                errors["lead_email"] = "Email address is required."

            # Gather team members
            team = []
            i = 0
            while True:
                tf = request.POST.get(f"team_{i}_first_name", "").strip()
                tl = request.POST.get(f"team_{i}_last_name", "").strip()
                te = request.POST.get(f"team_{i}_email", "").strip()
                if not tf and not tl and not te:
                    break
                if tf or te:
                    team.append({"first_name": tf, "last_name": tl, "email": te})
                i += 1

            if errors:
                context = self._build_context(request, step)
                context["errors"] = errors
                context["form_data"] = request.POST
                return render(request, WIZARD_TEMPLATES[step], context)

            wizard_data["lead_first_name"] = first_name
            wizard_data["lead_last_name"] = last_name
            wizard_data["lead_email"] = email
            wizard_data["team_members"] = team

        elif step == 2:
            checkboxes = [
                "read_intro", "read_step_by_step", "read_environment", "read_faq",
                "is_18", "free_workshop", "non_profit", "no_pay",
            ]
            all_checked = all(request.POST.get(cb) for cb in checkboxes)
            if not all_checked:
                context = self._build_context(request, step)
                context["error"] = "Please confirm all the checkboxes before proceeding."
                context["form_data"] = request.POST
                return render(request, WIZARD_TEMPLATES[step], context)
            wizard_data["prerequisites_confirmed"] = True

        elif step == 3:
            workshop_type = request.POST.get("workshop_type", "").strip()
            if workshop_type not in ("remote", "in_person"):
                context = self._build_context(request, step)
                context["error"] = "Please select a workshop type."
                return render(request, WIZARD_TEMPLATES[step], context)
            wizard_data["workshop_type"] = workshop_type

        elif step == 4:
            wizard_data["commitment_signed"] = True

        elif step == 5:
            experience = request.POST.get("experience", "")
            previous_event_id = request.POST.get("previous_event", "")

            wizard_data["has_organized_before"] = (experience == "yes")
            wizard_data["previous_event_id"] = previous_event_id if experience == "yes" else ""

            # Final step — save to database
            request.session["organize_wizard"] = wizard_data
            return self._save_application(request, wizard_data)

        request.session["organize_wizard"] = wizard_data
        next_step = step + 1
        return redirect("applications:organize_step", step=next_step)

    def _build_context(self, request, step):
        wizard_data = request.session.get("organize_wizard", {})
        return {
            "step": step,
            "total_steps": WIZARD_TOTAL_STEPS,
            "wizard_data": wizard_data,
            "form_data": {},
            "errors": {},
            "events": Event.objects.filter(published=True).order_by("-start_date"),
        }

    def _save_application(self, request, data):
        previous_event = None
        event_id = data.get("previous_event_id", "")
        if event_id:
            try:
                previous_event = Event.objects.get(pk=int(event_id))
            except (Event.DoesNotExist, ValueError):
                pass

        application = OrganizerApplication.objects.create(
            lead_first_name=data.get("lead_first_name", ""),
            lead_last_name=data.get("lead_last_name", ""),
            lead_email=data.get("lead_email", ""),
            team_members=data.get("team_members", []),
            prerequisites_confirmed=data.get("prerequisites_confirmed", False),
            workshop_type=data.get("workshop_type", "in_person"),
            commitment_signed=data.get("commitment_signed", False),
            has_organized_before=data.get("has_organized_before", False),
            previous_event=previous_event,
        )

        # Send emails
        from django.core.mail import send_mail
        from django.conf import settings
        
        organizer_name = f"{application.lead_first_name} {application.lead_last_name}".strip()
        organizer_email = application.lead_email
        admin_email = settings.DEFAULT_FROM_EMAIL

        # 1. Email to the organizer
        subject_organizer = "Your Python Weekend Organizer Application"
        message_organizer = (
            f"Hi {application.lead_first_name},\n\n"
            f"Thank you for volunteering to organize a Python Weekend workshop! "
            f"We have received your application and will review it shortly.\n\n"
            f"Best,\nThe Python Weekend Team"
        )
        try:
            send_mail(
                subject_organizer,
                message_organizer,
                settings.DEFAULT_FROM_EMAIL,
                [organizer_email],
                fail_silently=True,
            )
        except Exception:
            pass

        # 2. Email to the site admin
        subject_admin = f"New Organizer Application: {organizer_name}"
        message_admin = (
            f"A new organizer application has been submitted.\n\n"
            f"Lead Organizer: {organizer_name}\n"
            f"Email: {organizer_email}\n"
            f"Workshop Type: {application.get_workshop_type_display()}\n"
            f"Organized Before: {'Yes' if application.has_organized_before else 'No'}\n\n"
            f"Log in to the admin panel to review the full details."
        )
        try:
            send_mail(
                subject_admin,
                message_admin,
                settings.DEFAULT_FROM_EMAIL,
                [admin_email],
                fail_silently=True,
            )
        except Exception:
            pass

        # Clear wizard session
        request.session.pop("organize_wizard", None)
        return redirect("applications:organize_success")


class OrganizeSuccessView(View):
    def get(self, request):
        return render(request, "applications/organize/success.html")