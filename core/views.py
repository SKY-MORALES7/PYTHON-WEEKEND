# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.views import View
# from django.utils import timezone

# from content.models import Tutorial, BlogPost, Event
# from .forms import ContactForm


# class HomeView(View):
#     template_name = "core/home.html"

#     def get(self, request):
#         context = {
#             "tutorials": Tutorial.objects.filter(published=True).order_by("-created_at")[:3],
#             "blog_posts": BlogPost.objects.filter(published=True).order_by("-published_at")[:3],
#             "upcoming_events": Event.objects.filter(published=True, start_date__gte=timezone.now()).order_by("start_date")[:3],
#             "default_highlights": [
#                 {"icon": "🐍", "title": "Python fundamentals", "description": "Variables, loops, functions — the building blocks you'll use in every project."},
#                 {"icon": "🎸", "title": "Django from scratch", "description": "Models, views, templates. Build a real web app, not just 'Hello World'."},
#                 {"icon": "🚀", "title": "Deploy it", "description": "Get your project live by the end of day two. Something you can actually share."},
#             ],
#         }
#         return render(request, self.template_name, context)


# class AboutView(View):
#     template_name = "core/about.html"

#     def get(self, request):
#         return render(request, self.template_name)


# class ContactView(View):
#     template_name = "core/contact.html"

#     def get(self, request):
#         initial = {}
#         event_slug = request.GET.get("event")
#         if event_slug:
#             try:
#                 event = Event.objects.get(slug=event_slug, published=True)
#                 initial["interest"] = "attend"
#                 initial["message"] = f"I'm interested in attending the event: {event.title}"
#             except Event.DoesNotExist:
#                 pass
#         form = ContactForm(initial=initial)
#         return render(request, self.template_name, {"form": form})

#     def post(self, request):
#         form = ContactForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Thanks! We'll be in touch soon.")
#             return redirect("core:contact")
#         messages.error(request, "There were errors with your submission. Please correct the fields below.")
#         return render(request, self.template_name, {"form": form})


# def handler404(request, exception):
#     return render(request, "404.html", status=404)




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.utils import timezone
from django.conf import settings
from django.db.models import Count, Sum


from django.contrib.flatpages.models import FlatPage
from content.models import BlogPost, Event
from tutorials.models import Tutorial
from coach.models import Coach
from sponsors.models import Sponsor

from subscribers.models import Subscriber
from newsletter.models import Newsletter
from .forms import ContactForm
from .utils import send_contact_notifications, send_newsletter_welcome
from .security import validate_honeypot, check_rate_limit


def _footer_context():
    """Return counter variables used by the footer template on every page."""
    try:
        from applications.models import EventApplication
        now = timezone.now()
        published = Event.objects.filter(published=True)
        try:
            total_attendees = published.aggregate(s=Sum("attendees_count"))["s"] or 0
        except Exception:
            total_attendees = 0

        try:
            total_countries = (
                published.exclude(country="").values("country").distinct().count()
                or published.exclude(location="").values("location").distinct().count()
            ) or 0
        except Exception:
            total_countries = 0

        try:
            total_applicants = EventApplication.objects.count()
        except Exception:
            total_applicants = 0

        return {
            "total_upcoming_events": published.filter(start_date__gte=now).count(),
            "total_past_events":     published.filter(start_date__lt=now).count(),
            "total_applicants":      total_applicants,
            "total_attendees":       total_attendees,
            "total_countries":       total_countries,
        }
    except Exception:
        return {
            "total_upcoming_events": 0,
            "total_past_events": 0,
            "total_applicants": 0,
            "total_attendees": 0,
            "total_countries": 0,
        }


class HomeView(View):
    template_name = "core/home.html"

    def get(self, request):
        try:
            published_events = Event.objects.filter(published=True)
            upcoming_events  = published_events.filter(start_date__gte=timezone.now()).order_by("start_date")
        except Exception:
            published_events = Event.objects.none()
            upcoming_events  = Event.objects.none()

        try:
            total_events   = published_events.count()
        except Exception:
            total_events   = 0

        try:
            total_coaches  = Coach.objects.filter(active=True).count()
        except Exception:
            total_coaches  = 0

        try:
            total_cities   = (
                published_events
                .exclude(city="")
                .values("city")
                .distinct()
                .count()
            )
        except Exception:
            total_cities   = 0

        try:
            total_countries = (
                published_events
                .exclude(country="")
                .values("country")
                .distinct()
                .count()
            ) or (
                published_events
                .exclude(location="")
                .values("location")
                .distinct()
                .count()
            ) or 1
        except Exception:
            total_countries = 1

        try:
            coaches_list = Coach.objects.filter(active=True)[:3]
        except Exception:
            coaches_list = []

        try:
            blog_list = BlogPost.objects.filter(published=True).order_by("-published_at")[:3]
        except Exception:
            blog_list = []

        try:
            tutorials_list = Tutorial.objects.filter(published=True).order_by("-created_at")[:3]
        except Exception:
            tutorials_list = []

        try:
            sponsors_list = Sponsor.objects.filter(active=True)
        except Exception:
            sponsors_list = []

        context = {
            "total_events":          total_events,
            "total_coaches":         total_coaches,
            "total_cities":          total_cities,
            "total_countries":       total_countries,
            "upcoming_events":       upcoming_events[:6],
            "upcoming_events_total": upcoming_events.count() if hasattr(upcoming_events, "count") else 0,
            "coaches":               coaches_list,
            "blog_posts":            blog_list,
            "tutorials":             tutorials_list,
            "sponsors":              sponsors_list,
        }
        context.update(_footer_context())
        return render(request, self.template_name, context)


class AboutView(View):
    template_name = "core/about.html"

    def get(self, request):
        flatpage = FlatPage.objects.filter(url="/about/").first()
        context = {"flatpage": flatpage}
        context.update(_footer_context())
        return render(request, self.template_name, context)


class ContactView(View):
    template_name = "core/contact.html"

    def get(self, request):
        initial = {}
        event_slug = request.GET.get("event")
        if event_slug:
            try:
                event = Event.objects.get(slug=event_slug, published=True)
                initial["interest"] = "attend"
                initial["message"] = f"I'm interested in attending the event: {event.title}"
            except Event.DoesNotExist:
                pass
        form = ContactForm(initial=initial)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        # 1. Rate limit check: Prevent brute-force floods (staff exempt)
        is_allowed, _ = check_rate_limit(request, "contact_form", max_requests=5, window_seconds=600)
        if not is_allowed:
            messages.error(request, "You have submitted too many requests recently. Please wait a few minutes before trying again.")
            return redirect("core:contact")

        # 2. Honeypot check: If the hidden trap was filled or omitted by direct API bots, silently drop the request
        if "website" not in request.POST or not validate_honeypot(request, "website"):
            messages.success(request, "Thanks! We'll be in touch soon.")
            return redirect("core:contact")

        # 3. Spam content & duplicate detection filter
        email = request.POST.get("email", "").strip().lower()
        message_text = request.POST.get("message", "").lower()
        name = request.POST.get("name", "").lower()

        spam_keywords = ["search-pythonweekend", "seo rank", "increase traffic", "backlink", "casino", "viagra", "crypto", "marketing agency"]
        is_spam = any(kw in email or kw in message_text or kw in name for kw in spam_keywords)

        if not is_spam and email:
            from .models import ContactMessage
            # Check for identical duplicate message from same email
            duplicate_exists = ContactMessage.objects.filter(
                email__iexact=email,
                name__iexact=name
            ).exists()
            if duplicate_exists and ("williamphali" in name or "fausto" in name):
                is_spam = True

        if is_spam:
            messages.success(request, "Thanks! We'll be in touch soon.")
            return redirect("core:contact")

        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the submission object 
            contact_submission = form.save()
            
            # Fire off the email router! (Sends to staff only; auto-reflection to submitter is disabled)
            send_contact_notifications(contact_submission)
            
            messages.success(request, "Thanks! We'll be in touch soon.")
            return redirect("core:contact")
            
        messages.error(request, "There were errors with your submission. Please correct the fields below.")
        return render(request, self.template_name, {"form": form})



def handler404(request, exception):
    return render(request, "404.html", status=404)


class SubscribeView(View):
    def post(self, request):
        # 1. Honeypot check
        if not validate_honeypot(request, "website"):
            referer = request.META.get('HTTP_REFERER')
            return redirect(referer if referer else 'core:home')

        # 2. Rate limit check (staff exempt)
        is_allowed, _ = check_rate_limit(request, "newsletter_subscribe", max_requests=5, window_seconds=600)
        if not is_allowed:
            messages.error(request, "Too many requests. Please try again later.")
            referer = request.META.get('HTTP_REFERER')
            return redirect(referer if referer else 'core:home')

        email = request.POST.get("email", "").strip().lower()
        if email and "@" in email:
            subscriber = Subscriber.objects.filter(email__iexact=email).first()
            if not subscriber:
                subscriber = Subscriber.objects.create(email=email, is_active=True)
                send_newsletter_welcome(email, request=request)
                messages.success(request, "Thanks for subscribing! Check your inbox for a welcome email.")
            elif not subscriber.is_active:
                subscriber.is_active = True
                subscriber.save(update_fields=["is_active"])
                send_newsletter_welcome(email, request=request)
                messages.success(request, "Welcome back! Your subscription to Python Weekend Dispatch has been reactivated.")
            else:
                messages.info(request, "You're already subscribed to our newsletter!")
        else:
            messages.error(request, "Please provide a valid email address.")
        
        # Redirect back to where the user came from
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('core:home')


# ─── Phase 1 — New static pages ─────────────────────────────────────────────

class SupportView(View):
    template_name = "core/support.html"

    def get(self, request):
        flatpage = FlatPage.objects.filter(url__in=["/support/", "/support-us/"]).first()
        context = {
            "flatpage": flatpage,
            "upcoming_events": Event.objects.filter(published=True, start_date__gte=timezone.now()).order_by("start_date")[:6],
            "sponsors": Sponsor.objects.filter(active=True),
        }
        context.update(_footer_context())
        return render(request, self.template_name, context)


class PartnersView(View):
    template_name = "core/partners.html"

    def get(self, request):
        from django.db.models import Q
        flatpage = FlatPage.objects.filter(url="/partners/").first()
        all_sponsors = Sponsor.objects.filter(active=True)
        global_partners = all_sponsors.filter(Q(category="global") | (Q(category="") & Q(tier="platinum")))
        event_partners = all_sponsors.filter(Q(category="event") | (Q(category="") & Q(tier="gold")))
        community_partners = all_sponsors.filter(
            Q(category__in=["community_supporter", "community"]) | (Q(category="") & Q(tier__in=["silver", "community"]))
        )
        context = {
            "flatpage":           flatpage,
            "global_partners":    global_partners,
            "event_partners":     event_partners,
            "community_partners": community_partners,
        }
        context.update(_footer_context())
        return render(request, self.template_name, context)


class OrganiseView(View):
    template_name = "core/organise.html"

    def get(self, request):
        context = {}
        context.update(_footer_context())
        return render(request, self.template_name, context)


class ContributeView(View):
    template_name = "core/contribute.html"

    def get(self, request):
        flatpage = FlatPage.objects.filter(url="/contribute/").first()
        context = {"flatpage": flatpage}
        context.update(_footer_context())
        return render(request, self.template_name, context)


class ResourcesView(View):
    template_name = "core/resources.html"

    def get(self, request):
        flatpage = FlatPage.objects.filter(url="/resources/").first()
        from tutorials.models import Tutorial
        tutorials = Tutorial.objects.filter(published=True)
        context = {
            "flatpage": flatpage,
            "workshop_tutorials": tutorials.filter(slug="python-ai-tutorial") if hasattr(Tutorial, 'resource_type') else tutorials[:1],
            "organisers_manual":  tutorials.filter(resource_type="organisers_manual") if hasattr(Tutorial, 'resource_type') else None,
            "mentoring_guide":    tutorials.filter(resource_type="mentoring_guide") if hasattr(Tutorial, 'resource_type') else None,
            "extensions":         tutorials.filter(resource_type="extension") if hasattr(Tutorial, 'resource_type') else None,
        }
        context.update(_footer_context())
        return render(request, self.template_name, context)


class ResourceTutorialView(View):
    template_name = "core/resource_tutorial.html"

    def get(self, request):
        from tutorials.models import Tutorial
        tutorial_chapters = Tutorial.objects.filter(
            published=True,
            resource_type="workshop_tutorial"
        ).exclude(slug="python-ai-tutorial").order_by("id")
        context = {
            "tutorial_chapters": tutorial_chapters,
        }
        context.update(_footer_context())
        return render(request, self.template_name, context)


class ResourceManualView(View):
    template_name = "core/resource_manual.html"

    def get(self, request):
        context = {}
        context.update(_footer_context())
        return render(request, self.template_name, context)


class ResourceMentoringView(View):
    template_name = "core/resource_mentoring.html"

    def get(self, request):
        context = {}
        context.update(_footer_context())
        return render(request, self.template_name, context)


class ResourceExtensionsView(View):
    template_name = "core/resource_extensions.html"

    def get(self, request):
        context = {}
        context.update(_footer_context())
        return render(request, self.template_name, context)


class NewsletterView(View):
    template_name = "core/newsletter.html"

    def post(self, request):
        # 1. Honeypot check
        if not validate_honeypot(request, "website"):
            return redirect("core:newsletter")

        # 2. Rate limit check (staff exempt)
        is_allowed, _ = check_rate_limit(request, "newsletter_subscribe", max_requests=5, window_seconds=600)
        if not is_allowed:
            messages.error(request, "Too many requests. Please try again later.")
            return redirect("core:newsletter")

        email = request.POST.get("email", "").strip().lower()
        if email and "@" in email:
            subscriber = Subscriber.objects.filter(email__iexact=email).first()
            if not subscriber:
                subscriber = Subscriber.objects.create(email=email, is_active=True)
                send_newsletter_welcome(email, request=request)
                messages.success(request, "You're subscribed! Welcome to the Python Weekend Dispatch.")
            elif not subscriber.is_active:
                subscriber.is_active = True
                subscriber.save(update_fields=["is_active"])
                send_newsletter_welcome(email, request=request)
                messages.success(request, "Welcome back! Your subscription to Python Weekend Dispatch has been reactivated.")
            else:
                messages.info(request, "You're already subscribed to our newsletter!")
        else:
            messages.error(request, "Please provide a valid email address.")
        return redirect("core:newsletter")

    def get(self, request):
        past_editions = Newsletter.objects.filter(sent_at__isnull=False).order_by("-sent_at")
        context = {"past_editions": past_editions}
        context.update(_footer_context())
        return render(request, self.template_name, context)


class NewsletterUnsubscribeView(View):
    """
    Handles 1-click unsubscribe links embedded in all dispatch emails,
    plus self-service re-subscription.
    """
    template_name = "core/unsubscribed.html"

    def get(self, request, token=None):
        from .utils import verify_unsubscribe_token
        target_token = token or request.GET.get("token", "").strip()
        email = None
        status = "form"

        if target_token:
            email = verify_unsubscribe_token(target_token)
            if email:
                updated_count = Subscriber.objects.filter(email__iexact=email).update(is_active=False)
                status = "success"
            else:
                status = "invalid"

        context = {
            "email": email,
            "status": status,
            "token": target_token,
        }
        context.update(_footer_context())
        return render(request, self.template_name, context)

    def post(self, request, token=None):
        action = request.POST.get("action", "").strip()
        email = request.POST.get("email", "").strip().lower()

        if action == "resubscribe" and email and "@" in email:
            sub = Subscriber.objects.filter(email__iexact=email).first()
            if sub:
                sub.is_active = True
                sub.save(update_fields=["is_active"])
            else:
                Subscriber.objects.create(email=email, is_active=True)
            send_newsletter_welcome(email, request=request)
            messages.success(request, "You have successfully re-subscribed! Welcome back to Python Weekend Dispatch.")
            return redirect("core:newsletter")

        # Manual email unsubscribe
        if email and "@" in email:
            Subscriber.objects.filter(email__iexact=email).update(is_active=False)
            context = {
                "email": email,
                "status": "success",
            }
            context.update(_footer_context())
            return render(request, self.template_name, context)

        messages.error(request, "Please enter a valid email address.")
        return redirect("core:newsletter_unsubscribe")


class FAQView(View):
    template_name = "core/faq.html"

    def get(self, request):
        flatpage = FlatPage.objects.filter(url="/faq/").first()
        context = {"flatpage": flatpage}
        context.update(_footer_context())
        return render(request, self.template_name, context)


class CoCView(View):
    template_name = "core/coc.html"

    def get(self, request):
        flatpage = FlatPage.objects.filter(url="/code-of-conduct/").first()
        context = {"flatpage": flatpage}
        context.update(_footer_context())
        return render(request, self.template_name, context)


class JobsView(View):
    template_name = "core/jobs.html"

    def get(self, request):
        flatpage = FlatPage.objects.filter(url="/jobs/").first()
        context = {"flatpage": flatpage}
        context.update(_footer_context())
        return render(request, self.template_name, context)


import os
import re
from django.http import StreamingHttpResponse, Http404

class VideoStreamView(View):
    """Serve MP4 video with HTTP 206 Partial Content (Byte Range) support for seamless video playback."""
    def get(self, request):
        video_path = settings.BASE_DIR / "static" / "video" / "VID-20260523-WA0061.mp4"
        if not os.path.exists(video_path):
            raise Http404("Video file not found")

        file_size = os.path.getsize(video_path)
        range_header = request.META.get("HTTP_RANGE", "").strip()

        range_match = re.match(r"bytes=(\d+)-(\d+)?", range_header) if range_header else None

        if range_match:
            first_byte = int(range_match.group(1))
            last_byte = int(range_match.group(2)) if range_match.group(2) else file_size - 1
            if first_byte >= file_size:
                first_byte = file_size - 1
            length = last_byte - first_byte + 1

            def file_iterator(file_name, offset, len_bytes, chunk_size=8192):
                with open(file_name, "rb") as f:
                    f.seek(offset)
                    remaining = len_bytes
                    while remaining > 0:
                        read_len = min(remaining, chunk_size)
                        data = f.read(read_len)
                        if not data:
                            break
                        remaining -= len(data)
                        yield data

            response = StreamingHttpResponse(
                file_iterator(str(video_path), first_byte, length),
                status=206,
                content_type="video/mp4"
            )
            response["Content-Range"] = f"bytes {first_byte}-{last_byte}/{file_size}"
            response["Content-Length"] = str(length)
            response["Accept-Ranges"] = "bytes"
            return response
        else:
            def full_file_iterator(file_name, chunk_size=8192):
                with open(file_name, "rb") as f:
                    while True:
                        data = f.read(chunk_size)
                        if not data:
                            break
                        yield data

            response = StreamingHttpResponse(
                full_file_iterator(str(video_path)),
                content_type="video/mp4"
            )
            response["Content-Length"] = str(file_size)
            response["Accept-Ranges"] = "bytes"
            return response