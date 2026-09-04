from django.views.generic import ListView, DetailView
from .models import Tutorial

class TutorialListView(ListView):
    model = Tutorial
    template_name = "content/tutorial_list.html"
    paginate_by = 12

    def get_queryset(self):
        return Tutorial.objects.filter(published=True).order_by("-created_at")


class ResourceCategoryView(ListView):
    model = Tutorial
    template_name = "content/tutorial_list.html"
    paginate_by = 12
    resource_type = None
    page_title = "Resources"
    page_description = "Python Weekend learning materials."

    def get_queryset(self):
        qs = Tutorial.objects.filter(published=True).order_by("-created_at")
        if self.resource_type:
            qs = qs.filter(resource_type=self.resource_type)
        return qs
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["page_description"] = self.page_description
        return context


class TutorialDetailView(DetailView):
    model = Tutorial
    template_name = "content/tutorial_detail.html"
    context_object_name = "tutorial"

    def get_queryset(self):
        return Tutorial.objects.filter(published=True)
