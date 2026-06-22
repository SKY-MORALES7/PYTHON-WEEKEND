from django.views.generic import ListView, DetailView
from django.utils import timezone

from .models import BlogPost, Tutorial, Event


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


class TutorialListView(ListView):
    model = Tutorial
    template_name = "content/tutorial_list.html"
    paginate_by = 12

    def get_queryset(self):
        return Tutorial.objects.filter(published=True).order_by("-created_at")


class TutorialDetailView(DetailView):
    model = Tutorial
    template_name = "content/tutorial_detail.html"
    context_object_name = "tutorial"

    def get_queryset(self):
        return Tutorial.objects.filter(published=True)


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
