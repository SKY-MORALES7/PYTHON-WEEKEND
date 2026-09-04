from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    # ── Core ─────────────────────────────────────────────────────
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("subscribe/", views.SubscribeView.as_view(), name="subscribe"),

    # ── Support & Partners ────────────────────────────────────────
    path("support/", views.SupportView.as_view(), name="support"),
    path("partners/", views.PartnersView.as_view(), name="partners"),

    # ── Get Involved ─────────────────────────────────────────────
    path("organise/", views.OrganiseView.as_view(), name="organise"),
    path("contribute/", views.ContributeView.as_view(), name="contribute"),

    # ── Resources ────────────────────────────────────────────────
    path("resources/", views.ResourcesView.as_view(), name="resources"),

    # ── Community pages ──────────────────────────────────────────
    path("newsletter/", views.NewsletterView.as_view(), name="newsletter"),
    path("faq/", views.FAQView.as_view(), name="faq"),
    path("code-of-conduct/", views.CoCView.as_view(), name="coc"),
    path("jobs/", views.JobsView.as_view(), name="jobs"),
]
