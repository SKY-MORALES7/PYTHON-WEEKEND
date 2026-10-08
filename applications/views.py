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
            applicant_name = ""
            for question in application_form.questions.all():
                field_name = f"question_{question.pk}"
                val = form.cleaned_data.get(field_name, "")
                q_title = question.title.lower()
                if (question.question_type == "email" or "email" in q_title) and not applicant_email:
                    applicant_email = str(val).strip()
                if "name" in q_title and not applicant_name:
                    applicant_name = str(val).strip()

            # 1. Record in EventApplication for organizer review & approval
            from .models import EventApplication
            event_app = EventApplication.objects.create(
                event=application_form.event,
                form=application_form,
                full_name=applicant_name or "Applicant",
                email=applicant_email or "unknown@example.com",
                status="pending"
            )

            # 2. Save answers linked to this EventApplication
            form.save_answers(applicant_email=applicant_email or "unknown@example.com", application=event_app)

            # 3. Send confirmation email (using Form.confirmation_mail if specified)
            if applicant_email and "@" in applicant_email:
                try:
                    import threading
                    from django.conf import settings
                    from django.utils.html import escape
                    from core.utils import send_resend_email

                    site_name = getattr(settings, "SITE_NAME", "Python Weekend")
                    site_url = getattr(settings, "SITE_URL", "https://pythonweekend.org").rstrip("/")
                    event_title = application_form.event.title if application_form.event else "Python Weekend"
                    from_email = settings.DEFAULT_FROM_EMAIL

                    custom_text = application_form.confirmation_mail.strip() if application_form.confirmation_mail else ""
                    if not custom_text:
                        custom_text = (
                            f"Thank you for applying to attend {event_title}! "
                            f"We have received your application and will review it shortly. "
                            f"We will notify you by email once your application status has been updated."
                        )

                    subject = f"Application Received: {event_title}"
                    text_body = (
                        f"Hi {applicant_name or 'there'},\n\n"
                        f"{custom_text}\n\n"
                        f"Best regards,\nThe {site_name} Team\n"
                        f"{site_url}\n"
                    )

                    html_body = f"""<!DOCTYPE html>
<html>
<body style="margin: 0; padding: 24px 12px; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #16213e;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; background-color: #ffffff; border: 3px solid #16213e; box-shadow: 6px 6px 0px #16213e;">
          <tr>
            <td style="background-color: #16213e; padding: 24px 28px;">
              <span style="background-color: #0284c7; color: #ffffff; font-family: monospace; font-size: 11px; font-weight: bold; letter-spacing: 1.5px; text-transform: uppercase; padding: 4px 8px; border: 1.5px solid #16213e;">
                Application Received
              </span>
              <h1 style="color: #ffffff; margin: 12px 0 0 0; font-size: 22px; font-weight: 800;">{escape(event_title)}</h1>
            </td>
          </tr>
          <tr>
            <td style="padding: 28px; font-size: 15px; line-height: 1.6; color: #16213e;">
              <p style="margin: 0 0 16px 0;">Hi <strong>{escape(applicant_name or 'there')}</strong>,</p>
              <div style="white-space: pre-line; margin: 0 0 20px 0; color: #334155;">{escape(custom_text)}</div>
              <p style="margin: 0;">Warm regards,<br><strong>The {site_name} Team</strong></p>
            </td>
          </tr>
          <tr>
            <td style="background-color: #f8fafc; padding: 16px 28px; border-top: 2px solid #e2e8f0; font-size: 12px; color: #64748b;">
              Questions? Visit <a href="{site_url}" style="color: #0284c7; font-weight: bold;">{site_url}</a>.
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

                    def _send_confirmation():
                        try:
                            send_resend_email(
                                subject=subject,
                                message=text_body,
                                from_email=from_email,
                                recipient_list=[applicant_email],
                                html_message=html_body,
                            )
                        except Exception as e:
                            import logging
                            logging.getLogger(__name__).error(f"Failed to send confirmation_mail to {applicant_email}: {e}")

                    threading.Thread(target=_send_confirmation, daemon=True).start()
                except Exception as mail_err:
                    import logging
                    logging.getLogger(__name__).warning(f"Failed to queue attendee confirmation email: {mail_err}")

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

            raw_attendees = request.POST.get("expected_attendees", "").strip()
            try:
                expected_attendees = int(raw_attendees)
                if expected_attendees <= 0 or expected_attendees > 10000:
                    raise ValueError
            except (ValueError, TypeError):
                context = self._build_context(request, step)
                context["error"] = "Please select or enter a valid number of expected attendees (positive number)."
                context["form_data"] = request.POST
                return render(request, WIZARD_TEMPLATES[step], context)

            wizard_data["workshop_type"] = workshop_type
            wizard_data["expected_attendees"] = expected_attendees

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
                expected_attendees=int(data.get("expected_attendees", 50)),
                commitment_signed=data.get("commitment_signed", False),
                has_organized_before=data.get("has_organized_before", False),
                previous_event=previous_event,
                target_country=data.get("target_country", ""),
                target_state=data.get("target_state", ""),
            )

            # Send email notifications safely via background thread using Resend HTTPS API / SMTP fallback
            try:
                if is_email_sending_enabled():
                    import threading
                    from django.contrib.auth import get_user_model
                    from core.utils import send_resend_email
                    from django.utils.html import escape

                    User = get_user_model()
                    organizer_name = f"{application.lead_first_name} {application.lead_last_name}".strip()
                    organizer_email = application.lead_email
                    from_email = settings.DEFAULT_FROM_EMAIL
                    site_name = getattr(settings, 'SITE_NAME', 'Python Weekend')

                    # Prepare admin list
                    admin_emails = []
                    custom_inbox = getattr(settings, "CONTACT_NOTIFICATION_EMAIL", "").strip()
                    if custom_inbox:
                        admin_emails.append(custom_inbox)

                    superuser_emails = list(
                        User.objects.filter(is_superuser=True, is_active=True)
                        .exclude(email="")
                        .exclude(email__endswith="@example.com")
                        .values_list("email", flat=True)
                    )
                    for s_email in superuser_emails:
                        if s_email not in admin_emails:
                            admin_emails.append(s_email)

                    if not admin_emails:
                        admin_emails = [from_email]

                    # Personalize applicant message based on experience
                    if application.has_organized_before and application.previous_event:
                        exp_greeting = (
                            f"Thank you for volunteering to organize another {site_name} workshop! "
                            f"We are excited to see that you previously organized '{application.previous_event.title}' "
                            f"and would love to host another event."
                        )
                        exp_summary = f"Yes (Previously organized: {application.previous_event.title})"
                        location_html = ""
                        location_text = ""
                        admin_location_line = f"Previous Event: {application.previous_event.title}\n"
                    else:
                        loc_str = f"{application.target_state}, {application.target_country}".strip(", ")
                        loc_info = f" in {loc_str}" if loc_str else ""
                        exp_greeting = (
                            f"Thank you for volunteering to organize a {site_name} workshop{loc_info}!"
                        )
                        exp_summary = f"No (First-time organizer - Location: {loc_str or 'N/A'})"
                        if loc_str:
                            location_html = f"<strong>Location:</strong> {escape(loc_str)}<br>\n"
                            location_text = f"Location: {loc_str}\n"
                            admin_location_line = f"Country / Region: {loc_str}\n"
                        else:
                            location_html = ""
                            location_text = ""
                            admin_location_line = "Country / Region: N/A\n"

                    applicant_text = (
                        f"Hi {application.lead_first_name},\n\n"
                        f"{exp_greeting}\n\n"
                        f"We have received your application and our team will review it shortly. "
                        f"We will be in touch with organizer onboarding materials and next steps.\n\n"
                        f"Best regards,\nThe {site_name} Team\n"
                        f"{getattr(settings, 'SITE_URL', 'https://pythonweekend.org')}\n"
                    )

                    applicant_html = f"""<!DOCTYPE html>
<html>
<body style="margin: 0; padding: 24px 12px; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #16213e;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; background-color: #ffffff; border: 3px solid #16213e; box-shadow: 6px 6px 0px #16213e;">
          <tr>
            <td style="background-color: #16213e; padding: 24px 28px;">
              <span style="background-color: #0284c7; color: #ffffff; font-family: monospace; font-size: 11px; font-weight: bold; letter-spacing: 1.5px; text-transform: uppercase; padding: 4px 8px; border: 1.5px solid #16213e;">
                Organizer Application
              </span>
              <h1 style="color: #ffffff; margin: 12px 0 0 0; font-size: 22px; font-weight: 800;">Application Received!</h1>
            </td>
          </tr>
          <tr>
            <td style="padding: 28px; font-size: 15px; line-height: 1.6; color: #16213e;">
              <p style="margin: 0 0 16px 0;">Hi <strong>{escape(application.lead_first_name)}</strong>,</p>
              <p style="margin: 0 0 16px 0;">{escape(exp_greeting)}</p>
              <p style="margin: 0 0 16px 0;">We have received your application and our team is currently reviewing your proposal. We'll be in touch with onboarding materials, workshop timeline details, and next steps.</p>
              <div style="background-color: #f8fafc; border-left: 4px solid #0284c7; padding: 14px 18px; margin: 20px 0; font-size: 14px; color: #334155;">
                <strong>Workshop Type:</strong> {escape(application.get_workshop_type_display())}<br>
                <strong>Expected Attendees:</strong> {application.expected_attendees}<br>
                {location_html}<strong>Experience:</strong> {escape(exp_summary)}
              </div>
              <p style="margin: 0;">Warm regards,<br><strong>The {site_name} Team</strong></p>
            </td>
          </tr>
          <tr>
            <td style="background-color: #f8fafc; padding: 16px 28px; border-top: 2px solid #e2e8f0; font-size: 12px; color: #64748b;">
              Questions? Visit <a href="{getattr(settings, 'SITE_URL', 'https://pythonweekend.org')}" style="color: #0284c7; font-weight: bold;">{getattr(settings, 'SITE_URL', 'pythonweekend.org')}</a>.
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

                    admin_subject = f"New Organizer Application: {organizer_name} ({application.target_country or 'Global'})" if not (application.has_organized_before and application.previous_event) else f"Returning Organizer Application: {organizer_name} ({application.previous_event.title})"
                    admin_body = (
                        f"A new organizer application has been submitted on {site_name}.\n\n"
                        f"Lead Organizer: {organizer_name}\n"
                        f"Email: {organizer_email}\n"
                        f"Workshop Type: {application.get_workshop_type_display()}\n"
                        f"Expected Attendees: {application.expected_attendees}\n"
                        f"{admin_location_line}"
                        f"Organized Before: {exp_summary}\n\n"
                        f"Please log in to the admin panel to review and approve/reject the application."
                    )

                    def _send_organizer_emails():
                        try:
                            send_resend_email(
                                subject=f"Your {site_name} Organizer Application",
                                message=applicant_text,
                                from_email=from_email,
                                recipient_list=[organizer_email],
                                html_message=applicant_html,
                            )
                            logger.info(f"Organizer confirmation email successfully sent to {organizer_email}")
                        except Exception as m_err:
                            logger.error(f"Failed to send organizer confirmation email to {organizer_email}: {m_err}")

                        try:
                            send_resend_email(
                                subject=admin_subject,
                                message=admin_body,
                                from_email=from_email,
                                recipient_list=admin_emails,
                            )
                            logger.info(f"Organizer alert email successfully sent to staff: {admin_emails}")
                        except Exception as m_err2:
                            logger.error(f"Failed to send organizer admin alert to {admin_emails}: {m_err2}")

                        # Also notify co-organizers listed in team_members
                        for tm in (application.team_members or []):
                            tm_email = tm.get("email", "").strip() if isinstance(tm, dict) else ""
                            if not tm_email or tm_email.lower() == organizer_email.lower():
                                continue
                            tm_first = tm.get("first_name", "").strip() if isinstance(tm, dict) else ""
                            tm_last = tm.get("last_name", "").strip() if isinstance(tm, dict) else ""
                            tm_greeting_name = tm_first or "there"

                            co_subject = f"You have been selected as Co-Organizer for {site_name} by {organizer_name}"
                            co_text = (
                                f"Hi {tm_greeting_name},\n\n"
                                f"{organizer_name} ({organizer_email}) has submitted an application to organize a {site_name} workshop "
                                f"and selected you as a co-organizer!\n\n"
                                f"Workshop Type: {application.get_workshop_type_display()}\n"
                                f"{location_text}"
                                f"Lead Organizer: {organizer_name} ({organizer_email})\n\n"
                                f"Our team is currently reviewing the proposal. Once the event is approved by admin, you will receive "
                                f"your backend login credentials to help manage and organize the event.\n\n"
                                f"Best regards,\nThe {site_name} Team\n"
                                f"{getattr(settings, 'SITE_URL', 'https://pythonweekend.org')}\n"
                            )
                            co_html = f"""<!DOCTYPE html>
<html>
<body style="margin: 0; padding: 24px 12px; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #16213e;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; background-color: #ffffff; border: 3px solid #16213e; box-shadow: 6px 6px 0px #16213e;">
          <tr>
            <td style="background-color: #16213e; padding: 24px 28px;">
              <span style="background-color: #0284c7; color: #ffffff; font-family: monospace; font-size: 11px; font-weight: bold; letter-spacing: 1.5px; text-transform: uppercase; padding: 4px 8px; border: 1.5px solid #16213e;">
                Co-Organizer Notification
              </span>
              <h1 style="color: #ffffff; margin: 12px 0 0 0; font-size: 22px; font-weight: 800;">You're a Co-Organizer!</h1>
            </td>
          </tr>
          <tr>
            <td style="padding: 28px; font-size: 15px; line-height: 1.6; color: #16213e;">
              <p style="margin: 0 0 16px 0;">Hi <strong>{escape(tm_greeting_name)}</strong>,</p>
              <p style="margin: 0 0 16px 0;"><strong>{escape(organizer_name)}</strong> ({escape(organizer_email)}) has submitted an application to organize a {site_name} workshop and selected you as a <strong>co-organizer</strong>.</p>
              <div style="background-color: #f8fafc; border-left: 4px solid #0284c7; padding: 14px 18px; margin: 20px 0; font-size: 14px; color: #334155;">
                <strong>Workshop Type:</strong> {escape(application.get_workshop_type_display())}<br>
                {location_html}<strong>Lead Organizer:</strong> {escape(organizer_name)} ({escape(organizer_email)})
              </div>
              <p style="margin: 0 0 16px 0;">Our team is reviewing the workshop application. Once approved, you will receive an email with your backend login credentials to help manage the workshop.</p>
              <p style="margin: 0;">Warm regards,<br><strong>The {site_name} Team</strong></p>
            </td>
          </tr>
          <tr>
            <td style="background-color: #f8fafc; padding: 16px 28px; border-top: 2px solid #e2e8f0; font-size: 12px; color: #64748b;">
              Questions? Visit <a href="{getattr(settings, 'SITE_URL', 'https://pythonweekend.org')}" style="color: #0284c7; font-weight: bold;">{getattr(settings, 'SITE_URL', 'pythonweekend.org')}</a>.
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
                            try:
                                send_resend_email(
                                    subject=co_subject,
                                    message=co_text,
                                    from_email=from_email,
                                    recipient_list=[tm_email],
                                    html_message=co_html,
                                )
                                logger.info(f"Co-organizer notification sent to {tm_email}")
                            except Exception as co_err:
                                logger.error(f"Failed to send co-organizer notification to {tm_email}: {co_err}")

                    mail_thread = threading.Thread(target=_send_organizer_emails, daemon=True)
                    mail_thread.start()
            except Exception as mail_err:
                logger.warning(f"Failed to queue organizer email notifications: {mail_err}")

        except Exception as err:
            logger.error(f"Error saving organizer application to database: {err}", exc_info=True)

        # Clear wizard session and redirect to success page
        request.session.pop("organize_wizard", None)
        return redirect("applications:organize_success")


class OrganizeSuccessView(View):
    def get(self, request):
        return render(request, "applications/organize/success.html")