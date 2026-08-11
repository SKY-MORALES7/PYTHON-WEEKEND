import json
from django.views.generic import ListView, DetailView
from django.views import View
from django.utils import timezone
from django.http import HttpResponse

from .models import BlogPost, Event


class BlogListView(ListView):
    model = BlogPost
    template_name = "content/blog_list.html"
    paginate_by = 9

    def get_queryset(self):
        return BlogPost.objects.filter(published=True).order_by("-published_at")


class BlogDetailView(DetailView):
    model = BlogPost
    template_name = "content/blog_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return BlogPost.objects.filter(published=True)





class EventListView(ListView):
    model = Event
    template_name = "content/event_list.html"
    paginate_by = 9

    def get_queryset(self):
        now = timezone.now()
        return Event.objects.filter(published=True, start_date__gte=now).order_by("start_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context["past_events"] = Event.objects.filter(published=True, start_date__lt=now).order_by("-start_date")
        return context


class EventDetailView(DetailView):
    model = Event
    template_name = "content/event_detail.html"
    context_object_name = "event"

    def get_queryset(self):
        return Event.objects.filter(published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        # Per-event mentor, organiser and partner data (Phase 2 models)
        context["event_mentors"]   = event.event_mentors.select_related("coach").all()
        context["event_organisers"] = event.organisers.all()
        context["event_partners"]  = event.event_partners.all()
        return context


# ─── Phase 3: Event Map ───────────────────────────────────────────────────────

class EventMapView(View):
    template_name = "content/event_map.html"

    def get(self, request):
        from django.shortcuts import render
        all_events = Event.objects.filter(published=True).order_by("start_date")
        now = timezone.now()

        # Build a JSON-serialisable list for Leaflet
        map_events = []
        for e in all_events:
            if e.latitude and e.longitude:
                map_events.append({
                    "title":     e.title,
                    "city":      e.city or e.title,
                    "country":   e.country,
                    "date":      e.start_date.strftime("%d %b %Y"),
                    "url":       f"/content/events/{e.slug}/",
                    "lat":       float(e.latitude),
                    "lng":       float(e.longitude),
                    "upcoming":  e.start_date >= now,
                })

        context = {
            "map_events_json": json.dumps(map_events),
            "total_events":    all_events.count(),
        }
        return render(request, self.template_name, context)


# ─── Phase 3: ICAL export ────────────────────────────────────────────────────

class EventICALView(View):
    """Generates an RFC 5545 iCalendar feed of all upcoming published events."""

    def get(self, request):
        now = timezone.now()
        events = Event.objects.filter(published=True, start_date__gte=now).order_by("start_date")

        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Python Weekend//pythonweekend.org//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "X-WR-CALNAME:Python Weekend Events",
            "X-WR-CALDESC:Upcoming Python Weekend workshops",
            "X-WR-TIMEZONE:UTC",
        ]

        for e in events:
            dtstart = e.start_date.strftime("%Y%m%dT%H%M%SZ")
            dtend   = e.end_date.strftime("%Y%m%dT%H%M%SZ") if e.end_date else dtstart
            uid     = f"{e.slug}@pythonweekend.org"
            summary = self._ical_escape(e.title)
            location = self._ical_escape(e.venue_name or e.location or e.city or "")
            description = self._ical_escape(
                e.description[:200] if e.description else
                f"Python Weekend workshop in {e.city or e.location}. Free for selected participants."
            )
            url = f"https://pythonweekend.org/content/events/{e.slug}/"

            lines += [
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTART:{dtstart}",
                f"DTEND:{dtend}",
                f"SUMMARY:{summary}",
                f"LOCATION:{location}",
                f"DESCRIPTION:{description}",
                f"URL:{url}",
                "END:VEVENT",
            ]

        lines.append("END:VCALENDAR")
        cal_content = "\r\n".join(lines) + "\r\n"

        response = HttpResponse(cal_content, content_type="text/calendar; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="python-weekend-events.ics"'
        return response

    @staticmethod
    def _ical_escape(text):
        """Escape special characters for iCalendar fields."""
        return (
            str(text)
            .replace("\\", "\\\\")
            .replace(";", "\\;")
            .replace(",", "\\,")
            .replace("\n", "\\n")
        )
