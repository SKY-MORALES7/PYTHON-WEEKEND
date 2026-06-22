from django.urls import path
from . import views

app_name = "sponsors"

urlpatterns = [
    path("", views.SponsorListView.as_view(), name="list"),
]
