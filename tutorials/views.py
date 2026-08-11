from django.views.generic import ListView, DetailView
from .models import Tutorial

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
