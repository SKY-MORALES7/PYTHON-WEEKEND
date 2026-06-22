# import logging
# from django.core.mail import send_mail
# from django.conf import settings

# logger = logging.getLogger(__name__)

# def send_application_notifications(application):
#     """
#     Handles sending emails to the attendee (applicant) and internal stakeholders 
#     (organizers, coaches, sponsors) upon a new submission.
#     """
#     site_name = getattr(settings, 'SITE_NAME', 'Python Weekend')
    
#     # Define hardcoded email lists for your teams (or update as needed)
#     ORGANIZERS = ["kenter.yandev@gmail.com"]
#     COACHES = ["kenter.yandev@gmail.com"]
#     SPONSORS = ["kenter.yandev@gmail.com"]
    
#     staff_recipients = ORGANIZERS + COACHES + SPONSORS

#     # 1. Email Composition for the Attendee / Applicant
#     attendee_subject = f"Application Received: {site_name} - {application.city}"
#     attendee_message = (
#         f"Hello {application.full_name},\n\n"
#         f"Thank you for submitting your application for {site_name} in {application.city}, {application.country}.\n\n"
#         f"Our team is reviewing your application details (Expected attendees: {application.expected_attendees}). "
#         f"We will be in touch with you shortly regarding your application status.\n\n"
#         f"Best regards,\nThe {site_name} Team"
#     )

#     # 2. Email Composition for Stakeholders (Organizers, Coaches, Sponsors)
#     staff_subject = f"Alert: New Event Application for {application.city}"
#     staff_message = (
#         f"A new event application has been submitted on the platform.\n\n"
#         f"Applicant Details:\n"
#         f"- Name: {application.full_name}\n"
#         f"- Email: {application.email}\n"
#         f"- Location: {application.city}, {application.country}\n"
#         f"- Expected Attendees: {application.expected_attendees}\n"
#         f"- Motivation: {application.motivation}\n"
#         f"- Experience: {application.experience or 'None provided'}\n\n"
#         f"Please check the admin panel to update its status."
#     )

#     try:
#         # Send confirmation to the applicant
#         send_mail(
#             subject=attendee_subject,
#             message=attendee_message,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[application.email],
#             fail_silently=False,
#         )

#         # Broadcast update to organizers, coaches, and sponsors
#         if staff_recipients:
#             send_mail(
#                 subject=staff_subject,
#                 message=staff_message,
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=staff_recipients,
#                 fail_silently=False,
#             )
            
#     except Exception as e:
#         # Prevents application submission failure if the email server times out
#         logger.error(f"Failed to send email notifications for application {application.id}: {e}")

import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def send_status_update_email(application):
    """
    Fires an email to the applicant notifying them if their application 
    to organize an event was approved or rejected.
    """
    site_name = getattr(settings, 'SITE_NAME', 'Python Weekend')
    user_email = application.email
    user_name = application.full_name
    status = application.status

    if status == 'approved':
        subject = f"Congratulations! Your application for {site_name} has been approved 🎉"
        message_body = (
            f"Hi {user_name},\n\n"
            f"We have fantastic news! Your application to organize a {site_name} event has been approved.\n\n"
            f"Our team will reach out to you within the next 48 hours with onboarding materials, organizer guidelines, "
            f"and next steps to get your event rolling.\n\n"
            f"Welcome aboard!\n"
            f"The {site_name} Team"
        )
    elif status == 'rejected':
        subject = f"Update regarding your {site_name} Application"
        message_body = (
            f"Hi {user_name},\n\n"
            f"Thank you for your interest in organizing a {site_name} event and for taking the time to apply.\n\n"
            f"Unfortunately, we are unable to move forward with your application at this time. We receive many applications "
            f"and have to make difficult decisions based on location capacity and resource constraints.\n\n"
            f"We truly appreciate your support for the community and wish you the best of luck.\n\n"
            f"Warmly,\n"
            f"The {site_name} Team"
        )
    else:
        # If it moves back to pending, we don't need to send an automated message
        return

    try:
        send_mail(
            subject=subject,
            message=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Failed to send status update email for application {application.id}: {e}")


def send_application_notifications(application):
    """
    Handles sending emails to the attendee (applicant) and internal stakeholders
    (organizers, coaches, sponsors) upon a new submission.
    """
    site_name = getattr(settings, 'SITE_NAME', 'Python Weekend')
    # Define simple team recipient lists (adjust as needed)
    ORGANIZERS = ["kenter.yandev@gmail.com"]
    COACHES = ["kenter.yandev@gmail.com"]
    SPONSORS = ["kenter.yandev@gmail.com"]

    staff_recipients = ORGANIZERS + COACHES + SPONSORS

    # Applicant confirmation
    attendee_subject = f"Application Received: {site_name} - {getattr(application, 'city', '')}"
    attendee_message = (
        f"Hello {getattr(application, 'full_name', '')},\n\n"
        f"Thank you for submitting your application for {site_name} in {getattr(application, 'city', '')}, {getattr(application, 'country', '')}.\n\n"
        f"Our team is reviewing your application details (Expected attendees: {getattr(application, 'expected_attendees', 'N/A')}). "
        f"We will be in touch with you shortly regarding your application status.\n\n"
        f"Best regards,\nThe {site_name} Team"
    )

    # Staff notification
    staff_subject = f"Alert: New Event Application for {getattr(application, 'city', '')}"
    staff_message = (
        f"A new event application has been submitted on the platform.\n\n"
        f"Applicant Details:\n"
        f"- Name: {getattr(application, 'full_name', '')}\n"
        f"- Email: {getattr(application, 'email', '')}\n"
        f"- Location: {getattr(application, 'city', '')}, {getattr(application, 'country', '')}\n"
        f"- Expected Attendees: {getattr(application, 'expected_attendees', 'N/A')}\n"
        f"- Motivation: {getattr(application, 'motivation', '')}\n"
        f"- Experience: {getattr(application, 'experience', 'None provided')}\n\n"
        f"Please check the admin panel to update its status."
    )

    try:
        # Send confirmation to the applicant
        send_mail(
            subject=attendee_subject,
            message=attendee_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[getattr(application, 'email', '')],
            fail_silently=False,
        )

        # Send notification to staff
        if staff_recipients:
            send_mail(
                subject=staff_subject,
                message=staff_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=staff_recipients,
                fail_silently=False,
            )
    except Exception as e:
        logger.error(f"Failed to send email notifications for application {getattr(application, 'id', 'unknown')}: {e}")