from django.urls import path
from . import views

app_name = "coach"

urlpatterns = [
    path("", views.CoachListView.as_view(), name="list"),
]
