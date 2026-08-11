from django.urls import path
from . import views

app_name = "content"

urlpatterns = [
    # Blog
    path("blog/", views.BlogListView.as_view(), name="blog_list"),
    path("blog/<slug:slug>/", views.BlogDetailView.as_view(), name="blog_detail"),



    # Events — listing, map, ICAL & detail
    path("events/", views.EventListView.as_view(), name="event_list"),
    path("events/map/", views.EventMapView.as_view(), name="event_map"),
    path("events/ical/", views.EventICALView.as_view(), name="event_ical"),
    path("events/<slug:slug>/", views.EventDetailView.as_view(), name="event_detail"),
]
