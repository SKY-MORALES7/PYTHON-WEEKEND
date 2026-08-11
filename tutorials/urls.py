from django.urls import path
from . import views

app_name = "tutorials"

urlpatterns = [
    path("", views.TutorialListView.as_view(), name="tutorial_list"),
    path("<slug:slug>/", views.TutorialDetailView.as_view(), name="tutorial_detail"),
]
