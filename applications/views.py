# from django.shortcuts import render, redirect
# from django.views import View
# from django.contrib import messages

# from .forms import EventApplicationForm


# class EventApplicationView(View):
#     template_name = "applications/event_application.html"

#     def get(self, request):
#         form = EventApplicationForm()
#         return render(request, self.template_name, {"form": form})

#     def post(self, request):
#         form = EventApplicationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Application submitted — we'll review and be in touch.")
#             return redirect("applications:apply")
#         # Add a clean error message to the messages framework so users see a banner
#         messages.error(request, "There were errors with your submission. Please correct the fields below.")
#         return render(request, self.template_name, {"form": form})


# # Create your views here.
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages

from .forms import EventApplicationForm
from .utils import send_application_notifications  # Import your new dispatcher


class EventApplicationView(View):
    template_name = "applications/event_application.html"

    def get(self, request):
        form = EventApplicationForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = EventApplicationForm(request.POST)
        if form.is_valid():
            # Save data to database and get the object instance
            application = form.save()
            
            # Fire off emails dynamically
            send_application_notifications(application)
            
            messages.success(request, "Application submitted — we'll review and be in touch.")
            return redirect("applications:apply")
            
        # Add a clean error message to the messages framework so users see a banner
        messages.error(request, "There were errors with your submission. Please correct the fields below.")
        return render(request, self.template_name, {"form": form})