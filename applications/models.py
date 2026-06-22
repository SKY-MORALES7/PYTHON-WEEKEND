# from django.db import models
# from django.conf import settings

# class EventApplication(models.Model):
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('approved', 'Approved'),
#         ('rejected', 'Rejected'),
#     ]
    
 
#     full_name = models.CharField(max_length=100)
#     email = models.EmailField()
#     city = models.CharField(max_length=100)
#     country = models.CharField(max_length=100)
#     motivation = models.TextField()
#     experience = models.TextField(blank=True)
#     expected_attendees = models.PositiveIntegerField(default=50)

#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

#     def save(self, *args, **kwargs):
#         # 1. Check if this is an update to an existing record
#         if self.pk:
#             old_instance = EventApplication.objects.get(pk=self.pk)
#             # 2. Check if the status field specifically changed
#             if old_instance.status != self.status:
#                 from .utils import send_status_update_email
#                 send_status_update_email(self)
                
#         super().save(*args, **kwargs)

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.utils.text import slugify
from django.core.mail import send_mail
import logging

# Import the Event model from your content/events app
from content.models import Event  # 👈 Double-check that 'content' matches your event app name


class EventApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    motivation = models.TextField()
    experience = models.TextField(blank=True)
    expected_attendees = models.PositiveIntegerField(default=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def save(self, *args, **kwargs):
        # Check if this is an update to an existing record
        if self.pk:
            old_instance = EventApplication.objects.get(pk=self.pk)
            
            # Detect if the status field changed
            if old_instance.status != self.status:
                
                # ROUTINE A: Handle transition to APPROVED
                if self.status == 'approved':
                    logger = logging.getLogger(__name__)
                    default_password = "admin123"

                    # Build a base username and ensure uniqueness
                    base_username = slugify(self.email.split('@')[0]) or 'organizer'
                    username = base_username
                    suffix = 0
                    while User.objects.filter(username=username).exists():
                        suffix += 1
                        username = f"{base_username}{suffix}"

                    try:
                        user = User.objects.create_user(
                            username=username,
                            email=self.email,
                            password=default_password,
                            is_staff=True
                        )

                        # Ensure the Organizers group has proper permissions for Event
                        from django.contrib.contenttypes.models import ContentType
                        from django.contrib.auth.models import Permission

                        group, created = Group.objects.get_or_create(name="Organizers")
                        content_type = ContentType.objects.get_for_model(Event)
                        permissions = Permission.objects.filter(content_type=content_type)
                        # Always ensure the group has the right event permissions
                        group.permissions.set(permissions)
                        user.groups.add(group)

                        # Create a starter Event owned by this user
                        Event.objects.create(
                            title=f"Python Weekend - {self.city}",
                            slug=slugify(f"python-weekend-{self.city}-{user.id}"),
                            start_date=timezone.now() + timezone.timedelta(days=60),
                            end_date=timezone.now() + timezone.timedelta(days=62),
                            city=self.city,
                            location=f"{self.city}, {self.country}",
                            owner=user,
                            published=False
                        )

                        # Email credentials to the applicant
                        try:
                            logger.info(f"Provisioning organizer credentials -> recipient={self.email} username={username}")
                            subject = f"Your organizer account for {getattr(settings, 'SITE_NAME', 'Python Weekend')}"
                            message = (
                                f"Hi {self.full_name},\n\n"
                                f"Your application was approved. You can sign in to manage your event with the following credentials:\n\n"
                                f"Username: {username}\n"
                                f"Password: {default_password}\n\n"
                                f"Please change your password after first login.\n\n"
                                f"Best,\nThe Team"
                            )
                            send_mail(subject=subject, message=message, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[self.email], fail_silently=False)
                        except Exception as e:
                            logger.error(f"Failed to send credentials email for application {getattr(self, 'id', 'unknown')}: {e}")

                        # Also trigger existing status notification (keeps previous behavior)
                        from .utils import send_status_update_email
                        send_status_update_email(self)

                    except Exception as e:
                        logger.error(f"Failed to provision organizer user for application {getattr(self, 'id', 'unknown')}: {e}")

                # ROUTINE B: Handle transition to REJECTED
                elif self.status == 'rejected':
                    from .utils import send_status_update_email
                    send_status_update_email(self)
                
        super().save(*args, **kwargs)