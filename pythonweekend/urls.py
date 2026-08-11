from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Core pages: home, about, contact, and all new static pages
    path("", include("core.urls", namespace="core")),

    # Content: blog, events (under /content/ prefix — canonical)
    path("content/", include("content.urls", namespace="content")),

    # Tutorials
    path("tutorials/", include("tutorials.urls", namespace="tutorials")),

    # Root-level event aliases (clean URLs for nav and footer)
    path("events/", RedirectView.as_view(url="/content/events/", permanent=False), name="events_root"),
    path("events/map/", RedirectView.as_view(url="/content/events/map/", permanent=False), name="events_map_root"),
    path("events/ical/", RedirectView.as_view(url="/content/events/ical/", permanent=False), name="events_ical_root"),

    # Community
    path("coaches/", include("coach.urls", namespace="coach")),
    path("sponsors/", include("sponsors.urls", namespace="sponsors")),
    path("applications/", include("applications.urls", namespace="applications")),

    # Flatpages (Terms, Privacy)
    path("pages/", include("django.contrib.flatpages.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = "core.views.handler404"
