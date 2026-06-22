from django import forms

from .models import EventApplication


class EventApplicationForm(forms.ModelForm):
    class Meta:
        model = EventApplication
        fields = [
            "full_name",
            "email",
            "city",
            "country",
            "motivation",
            "experience",
            "expected_attendees",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "w-full bg-tactical border border-shield-navy/60 focus:border-shield-ice/60 rounded-lg px-4 py-2.5 text-shield-star placeholder-shield-steel outline-none transition-colors text-sm"}),
            "email": forms.EmailInput(attrs={"class": "w-full bg-tactical border border-shield-navy/60 focus:border-shield-ice/60 rounded-lg px-4 py-2.5 text-shield-star placeholder-shield-steel outline-none transition-colors text-sm"}),
            "city": forms.TextInput(attrs={"class": "w-full bg-tactical border border-shield-navy/60 focus:border-shield-ice/60 rounded-lg px-4 py-2.5 text-shield-star placeholder-shield-steel outline-none transition-colors text-sm"}),
            "country": forms.TextInput(attrs={"class": "w-full bg-tactical border border-shield-navy/60 focus:border-shield-ice/60 rounded-lg px-4 py-2.5 text-shield-star placeholder-shield-steel outline-none transition-colors text-sm"}),
            "motivation": forms.Textarea(attrs={"class": "w-full bg-tactical border border-shield-navy/60 focus:border-shield-ice/60 rounded-lg px-4 py-2.5 text-shield-star placeholder-shield-steel outline-none transition-colors text-sm", "rows": 5}),
            "experience": forms.Textarea(attrs={"class": "w-full bg-tactical border border-shield-navy/60 focus:border-shield-ice/60 rounded-lg px-4 py-2.5 text-shield-star placeholder-shield-steel outline-none transition-colors text-sm", "rows": 4}),
            "expected_attendees": forms.NumberInput(attrs={"class": "w-full bg-tactical border border-shield-navy/60 focus:border-shield-ice/60 rounded-lg px-4 py-2.5 text-shield-star placeholder-shield-steel outline-none transition-colors text-sm"}),
        }

    def clean_full_name(self):
        name = self.cleaned_data.get("full_name", "").strip()
        # Reject names that are only numeric or contain digits
        if any(char.isdigit() for char in name):
            raise forms.ValidationError("Full name must not contain numbers.")
        if len(name) < 2:
            raise forms.ValidationError("Please provide your full name.")
        return name
