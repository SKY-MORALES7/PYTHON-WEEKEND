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
    path("resources/", include("tutorials.urls", namespace="tutorials")),

    # Root-level event & organizer aliases (clean URLs for nav and footer)
    path("events/", RedirectView.as_view(url="/content/events/", permanent=False), name="events_root"),
    path("events/map/", RedirectView.as_view(url="/content/events/map/", permanent=False), name="events_map_root"),
    path("events/ical/", RedirectView.as_view(url="/content/events/ical/", permanent=False), name="events_ical_root"),
    path("blog/", RedirectView.as_view(url="/content/blog/", permanent=False), name="blog_root"),
    path("coc/", RedirectView.as_view(url="/code-of-conduct/", permanent=False), name="coc_root"),
    path("apply/organise/", RedirectView.as_view(url="/applications/organize/", permanent=False)),
    path("apply/organize/", RedirectView.as_view(url="/applications/organize/", permanent=False)),
    path("organise/", RedirectView.as_view(url="/applications/organize/", permanent=False)),
    path("organize/", RedirectView.as_view(url="/applications/organize/", permanent=False)),


    # Community
    path("coaches/", include("coach.urls", namespace="coach")),
    path("sponsors/", include("sponsors.urls", namespace="sponsors")),
    path("applications/", include("applications.urls", namespace="applications")),

    # Flatpages (Terms, Privacy)
    path("pages/", include("django.contrib.flatpages.urls")),
]

from django.urls import re_path
from django.views.static import serve

# Serve media files (useful for local testing and simple deployments without S3)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]

# Custom error handlers
handler404 = "core.views.handler404"

# Customize Admin Site
admin.site.site_header = "Python Weekend Administration"
admin.site.site_title = "Python Weekend Admin"
admin.site.index_title = "Welcome to the Python Weekend Dashboard"
