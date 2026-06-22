from django.views.generic import ListView
from .models import Coach


class CoachListView(ListView):
    model = Coach
    template_name = "coach/list.html"
    context_object_name = "coaches"

    def get_queryset(self):
        return Coach.objects.filter(active=True).order_by("name")
