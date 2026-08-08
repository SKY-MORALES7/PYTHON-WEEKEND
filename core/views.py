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
from django.db.models import Count

from content.models import Tutorial, BlogPost, Event
from coach.models import Coach
from sponsors.models import Sponsor

from .models import Subscriber
from .forms import ContactForm
from .utils import send_contact_notifications, send_newsletter_welcome


class HomeView(View):
    template_name = "core/home.html"

    def get(self, request):
        published_events = Event.objects.filter(published=True)
        upcoming_events  = published_events.filter(start_date__gte=timezone.now()).order_by("start_date")

        # Impact stats
        total_events   = published_events.count()
        total_coaches  = Coach.objects.filter(active=True).count()
        # Distinct non-empty cities
        total_cities   = (
            published_events
            .exclude(city="")
            .values("city")
            .distinct()
            .count()
        )
        # Distinct non-empty locations used as country proxy until a country field is added
        total_countries = (
            published_events
            .exclude(location="")
            .values("location")
            .distinct()
            .count()
        ) or 1

        context = {
            # Dynamic stats
            "total_events":    total_events,
            "total_coaches":   total_coaches,
            "total_cities":    total_cities,
            "total_countries": total_countries,
            # Upcoming events — show up to 6 on home page
            "upcoming_events":       upcoming_events[:6],
            "upcoming_events_total": upcoming_events.count(),
            # Coaches spotlight — first 3 active coaches
            "coaches": Coach.objects.filter(active=True)[:3],
            # Blog
            "blog_posts": BlogPost.objects.filter(published=True).order_by("-published_at")[:3],
            # Tutorials (kept for potential future use)
            "tutorials": Tutorial.objects.filter(published=True).order_by("-created_at")[:3],
            # Sponsors
            "sponsors": Sponsor.objects.filter(active=True),
        }
        return render(request, self.template_name, context)


class AboutView(View):
    template_name = "core/about.html"

    def get(self, request):
        return render(request, self.template_name)


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
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the submission object 
            contact_submission = form.save()
            
            # Fire off the email router!
            send_contact_notifications(contact_submission)
            
            messages.success(request, "Thanks! We'll be in touch soon.")
            return redirect("core:contact")
            
        messages.error(request, "There were errors with your submission. Please correct the fields below.")
        return render(request, self.template_name, {"form": form})


def handler404(request, exception):
    return render(request, "404.html", status=404)


class SubscribeView(View):
    def post(self, request):
        email = request.POST.get("email")
        if email:
            subscriber, created = Subscriber.objects.get_or_create(email=email)
            if created:
                send_newsletter_welcome(email)
                messages.success(request, "Thanks for subscribing! Check your inbox for a welcome email.")
            else:
                messages.info(request, "You're already subscribed to our newsletter!")
        else:
            messages.error(request, "Please provide a valid email address.")
        
        # Redirect back to where the user came from
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('core:home')