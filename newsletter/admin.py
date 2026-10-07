from django.contrib import admin, messages
from django.utils import timezone
from .models import Newsletter, NewsletterSubscriber
from subscribers.models import Subscriber
from core.utils import send_newsletter_broadcast

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("subject", "sent_at", "created_at")
    list_filter = ("sent_at",)
    search_fields = ("subject", "content")
    actions = ["send_newsletter_to_subscribers"]

    def save_model(self, request, obj, form, change):
        is_new = not change
        super().save_model(request, obj, form, change)
        if is_new:
            count = send_newsletter_broadcast(obj, request=request)
            if count > 0:
                self.message_user(
                    request,
                    f"Newsletter '{obj.subject}' was created and queued for delivery to {count} active subscriber(s). Each email includes a personalized unsubscribe link.",
                    level=messages.SUCCESS,
                )
            else:
                self.message_user(
                    request,
                    f"Newsletter '{obj.subject}' was saved. No active subscribers found to send to.",
                    level=messages.WARNING,
                )

    def send_newsletter_to_subscribers(self, request, queryset):
        active_count = Subscriber.objects.filter(is_active=True).count()
        if active_count == 0:
            self.message_user(request, "No active subscribers found.", level=messages.WARNING)
            return

        total_queued = 0
        for newsletter in queryset:
            count = send_newsletter_broadcast(newsletter, request=request)
            total_queued += count

        self.message_user(
            request,
            f"Successfully queued {queryset.count()} newsletter edition(s) for delivery to {active_count} active subscriber(s) with personalized unsubscribe links.",
            level=messages.SUCCESS,
        )

    send_newsletter_to_subscribers.short_description = "Send selected newsletter(s) to all active subscribers"

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "subscribed_at")
    list_filter = ("is_active",)
    search_fields = ("email",)
