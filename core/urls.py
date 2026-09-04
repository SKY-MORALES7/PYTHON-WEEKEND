from django.urls import path
from . import views
from tutorials.views import ResourceCategoryView

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
    path("resources/tutorial/", ResourceCategoryView.as_view(
        resource_type="workshop_tutorial", 
        page_title="Python & AI Tutorial", 
        page_description="The official step-by-step guide used in Python Weekend workshops."
    ), name="resource_tutorial"),
    path("resources/manual/", ResourceCategoryView.as_view(
        resource_type="organisers_manual", 
        page_title="Organiser's Manual", 
        page_description="A complete guide to planning and running a successful Python Weekend."
    ), name="resource_manual"),
    path("resources/mentoring/", ResourceCategoryView.as_view(
        resource_type="mentoring_guide", 
        page_title="Mentoring Guide", 
        page_description="Best practices for supporting beginners and creating a welcoming environment."
    ), name="resource_mentoring"),
    path("resources/extensions/", ResourceCategoryView.as_view(
        resource_type="extension", 
        page_title="Tutorial Extensions", 
        page_description="Advanced exercises and projects for continuing your learning journey."
    ), name="resource_extensions"),

    # ── Community pages ──────────────────────────────────────────
    path("newsletter/", views.NewsletterView.as_view(), name="newsletter"),
    path("faq/", views.FAQView.as_view(), name="faq"),
    path("code-of-conduct/", views.CoCView.as_view(), name="coc"),
    path("jobs/", views.JobsView.as_view(), name="jobs"),
]
