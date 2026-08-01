from django.urls import path
from .views import ApplicationFormView, OrganizeWizardView, OrganizeSuccessView

app_name = "applications"

urlpatterns = [
    path("apply/<int:form_id>/", ApplicationFormView.as_view(), name="apply"),

    # Organizer application wizard
    path("organize/", OrganizeWizardView.as_view(), name="organize_start"),
    path("organize/step/<int:step>/", OrganizeWizardView.as_view(), name="organize_step"),
    path("organize/success/", OrganizeSuccessView.as_view(), name="organize_success"),
]
