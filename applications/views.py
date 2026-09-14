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
        from core.security import check_rate_limit
        is_allowed, _ = check_rate_limit(request, "event_application", max_requests=5, window_seconds=600)
        if not is_allowed:
            from django.contrib import messages
            messages.error(request, "Too many applications submitted recently. Please wait a few minutes before trying again.")
            return redirect("applications:apply", form_id=form_id)

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
            from core.security import check_rate_limit, validate_honeypot
            if not validate_honeypot(request, "website"):
                # Bot detected — silently pretend success to prevent spam and protect email quotas
                return redirect("applications:organize_step", step=2)

            is_allowed, _ = check_rate_limit(request, "organize_wizard", max_requests=10, window_seconds=600)
            if not is_allowed:
                context = self._build_context(request, step)
                context["error"] = "Too many requests. Please wait a few minutes before trying again."
                return render(request, WIZARD_TEMPLATES[step], context)

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
            target_country = request.POST.get("target_country", "").strip()
            target_state = request.POST.get("target_state", "").strip()
            target_country_custom = request.POST.get("target_country_custom", "").strip()
            target_state_custom = request.POST.get("target_state_custom", "").strip()

            if not experience:
                context = self._build_context(request, step)
                context["error"] = "Please select an option indicating whether you have organized Python Weekend before."
                return render(request, WIZARD_TEMPLATES[step], context)

            if experience == "yes":
                if not previous_event_id:
                    context = self._build_context(request, step)
                    context["error"] = "You selected that you have organized Python Weekend before. Please choose the previous event you organized."
                    return render(request, WIZARD_TEMPLATES[step], context)

                try:
                    prev_ev = Event.objects.get(pk=int(previous_event_id))
                except (Event.DoesNotExist, ValueError):
                    context = self._build_context(request, step)
                    context["error"] = "The selected previous event could not be found. Please select a valid event."
                    return render(request, WIZARD_TEMPLATES[step], context)

                wizard_data["has_organized_before"] = True
                wizard_data["previous_event_id"] = previous_event_id
                wizard_data["target_country"] = ""
                wizard_data["target_state"] = ""
                wizard_data["target_country_custom"] = ""
                wizard_data["target_state_custom"] = ""
            else:
                final_country = target_country_custom if target_country == "Other" else target_country
                final_state = target_state_custom if target_country == "Other" else target_state

                if not final_country or not final_state:
                    context = self._build_context(request, step)
                    context["error"] = "Please select or enter your target Country and State / Region."
                    return render(request, WIZARD_TEMPLATES[step], context)

                wizard_data["has_organized_before"] = False
                wizard_data["previous_event_id"] = ""
                wizard_data["target_country"] = final_country
                wizard_data["target_state"] = final_state
                wizard_data["target_country_custom"] = target_country_custom
                wizard_data["target_state_custom"] = target_state_custom

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
        import logging
        from django.core.mail import send_mail
        from django.conf import settings
        from django.contrib.auth import get_user_model
        from core.security import is_email_sending_enabled

        logger = logging.getLogger(__name__)

        if not data.get("lead_email") or not data.get("lead_first_name"):
            context = self._build_context(request, 5)
            context["error"] = "Your session expired or contact info is missing. Please start from Step 1."
            return render(request, WIZARD_TEMPLATES[5], context)

        try:
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
                target_country=data.get("target_country", ""),
                target_state=data.get("target_state", ""),
            )

            # Send email notifications safely
            try:
                if is_email_sending_enabled():
                    User = get_user_model()
                    organizer_name = f"{application.lead_first_name} {application.lead_last_name}".strip()
                    organizer_email = application.lead_email

                    admin_emails = list(User.objects.filter(is_superuser=True, is_active=True).exclude(email='').values_list('email', flat=True))
                    if not admin_emails:
                        admin_emails = [settings.DEFAULT_FROM_EMAIL]

                    # Personalize applicant message based on experience
                    if application.has_organized_before and application.previous_event:
                        applicant_msg = (
                            f"Hi {application.lead_first_name},\n\n"
                            f"Thank you for volunteering to organize another Python Weekend workshop!\n\n"
                            f"We are excited to see that you previously organized '{application.previous_event.title}' "
                            f"and would love to host another event. We have received your application and our team will review it shortly.\n\n"
                            f"Best regards,\nThe Python Weekend Team"
                        )
                        exp_summary = f"Yes (Previously organized: {application.previous_event.title})"
                    else:
                        loc_str = f"{application.target_state}, {application.target_country}".strip(", ")
                        loc_info = f" in {loc_str}" if loc_str else ""
                        applicant_msg = (
                            f"Hi {application.lead_first_name},\n\n"
                            f"Thank you for volunteering to organize a Python Weekend workshop{loc_info}!\n\n"
                            f"We have received your application and our team will review it shortly.\n\n"
                            f"Best regards,\nThe Python Weekend Team"
                        )
                        exp_summary = f"No (First-time organizer - Location: {loc_str or 'N/A'})"

                    try:
                        send_mail(
                            "Your Python Weekend Organizer Application",
                            applicant_msg,
                            settings.DEFAULT_FROM_EMAIL,
                            [organizer_email],
                            fail_silently=True,
                        )
                    except Exception as mail_err1:
                        logger.warning(f"Could not send applicant confirmation email: {mail_err1}")

                    try:
                        send_mail(
                            f"New Organizer Application: {organizer_name}",
                            (
                                f"A new organizer application has been submitted.\n\n"
                                f"Lead Organizer: {organizer_name}\n"
                                f"Email: {organizer_email}\n"
                                f"Workshop Type: {application.get_workshop_type_display()}\n"
                                f"Organized Before: {exp_summary}\n\n"
                                f"Please log in to the admin panel to review and approve/reject the application."
                            ),
                            settings.DEFAULT_FROM_EMAIL,
                            admin_emails,
                            fail_silently=True,
                        )
                    except Exception as mail_err2:
                        logger.warning(f"Could not send admin notification email: {mail_err2}")
            except Exception as mail_err:
                logger.warning(f"Failed to process email notifications: {mail_err}")

        except Exception as err:
            logger.error(f"Error saving organizer application to database: {err}", exc_info=True)

        # Clear wizard session and redirect to success page
        request.session.pop("organize_wizard", None)
        return redirect("applications:organize_success")


class OrganizeSuccessView(View):
    def get(self, request):
        return render(request, "applications/organize/success.html")