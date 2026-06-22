from django.urls import path
from .views import EventApplicationView

app_name = "applications"

urlpatterns = [
    path("apply/", EventApplicationView.as_view(), name="apply"),
]


