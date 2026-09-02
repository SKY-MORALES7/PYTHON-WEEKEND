from django.contrib import admin, messages
from django.core.mail import send_mass_mail
from django.conf import settings
from django.utils import timezone
from .models import Newsletter, NewsletterSubscriber
from subscribers.models import Subscriber

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("subject", "sent_at", "created_at")
    list_filter = ("sent_at",)
    search_fields = ("subject", "content")
    actions = ["send_newsletter_to_subscribers"]

    def send_newsletter_to_subscribers(self, request, queryset):
        active_subscribers = list(Subscriber.objects.filter(is_active=True).values_list('email', flat=True))
        if not active_subscribers:
            self.message_user(request, "No active subscribers found.", level=messages.WARNING)
            return

        total_sent = 0
        for newsletter in queryset:
            email_messages = [
                (
                    newsletter.subject,
                    newsletter.content,
                    settings.DEFAULT_FROM_EMAIL,
                    [sub_email]
                )
                for sub_email in active_subscribers
            ]
            try:
                send_mass_mail(email_messages, fail_silently=False)
                newsletter.sent_at = timezone.now()
                newsletter.save()
                total_sent += len(active_subscribers)
            except Exception as e:
                self.message_user(request, f"Error sending newsletter '{newsletter.subject}': {e}", level=messages.ERROR)

        if total_sent > 0:
            self.message_user(request, f"Successfully sent newsletter to {total_sent} subscriber(s).", level=messages.SUCCESS)

    send_newsletter_to_subscribers.short_description = "Send selected newsletter(s) to all active subscribers"

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "subscribed_at")
    list_filter = ("is_active",)
    search_fields = ("email",)
