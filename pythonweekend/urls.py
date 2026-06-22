from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Core pages: home, about, contact
    path("", include("core.urls", namespace="core")),

    # Content: blog, tutorials, events (under /content/ prefix)
    path("content/", include("content.urls", namespace="content")),

    # Community
    path("coaches/", include("coach.urls", namespace="coach")),
    path("sponsors/", include("sponsors.urls", namespace="sponsors")),
    path("applications/", include("applications.urls", namespace="applications")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = "core.views.handler404"
