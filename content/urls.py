from django.urls import path
from . import views

app_name = "content"

urlpatterns = [
    # Blog
    path("blog/", views.BlogListView.as_view(), name="blog_list"),
    path("blog/<slug:slug>/", views.BlogDetailView.as_view(), name="blog_detail"),

    # Tutorials
    path("tutorials/", views.TutorialListView.as_view(), name="tutorial_list"),
    path("tutorials/<slug:slug>/", views.TutorialDetailView.as_view(), name="tutorial_detail"),

    # Events — listing & detail only; creation is admin-only
    path("events/", views.EventListView.as_view(), name="event_list"),
    path("events/<slug:slug>/", views.EventDetailView.as_view(), name="event_detail"),
]
