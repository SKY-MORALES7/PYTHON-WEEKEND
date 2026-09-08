from django import forms
import re


INTEREST_CHOICES = [
    ("attend", "Attend an event"),
    ("coach", "Volunteer as a coach"),
    ("sponsor", "Sponsor Python Weekend"),
    ("other", "Something else"),
]


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "w-full bg-tactical border border-shield-navy/60 focus:border-shield-ice/60 rounded-lg px-4 py-2.5 text-shield-star placeholder-shield-steel outline-none transition-colors text-sm",
            "placeholder": "Your name",
        }),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "w-full bg-tactical border border-shield-navy/60 focus:border-shield-ice/60 rounded-lg px-4 py-2.5 text-shield-star placeholder-shield-steel outline-none transition-colors text-sm",
            "placeholder": "you@example.com",
        }),
    )
    interest = forms.ChoiceField(
        choices=INTEREST_CHOICES,
        widget=forms.Select(attrs={
            "class": "w-full bg-tactical border border-shield-navy/60 focus:border-shield-ice/60 rounded-lg px-4 py-2.5 text-shield-star outline-none transition-colors text-sm",
        }),
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "w-full bg-tactical border border-shield-navy/60 focus:border-shield-ice/60 rounded-lg px-4 py-2.5 text-shield-star placeholder-shield-steel outline-none transition-colors text-sm",
            "rows": 5,
            "placeholder": "Tell us more…",
        }),
    )

    # ── Invisible honeypot trap for bots ──────────────────────────────────────
    # Humans will never see or interact with this field. Bots blindly fill it out.
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "style": "display:none !important; position:absolute; left:-9999px;",
            "tabindex": "-1",
            "autocomplete": "off",
            "aria-hidden": "true",
        }),
    )

    def save(self):
        """Persist the submission to the ContactMessage model."""
        from .models import ContactMessage

        return ContactMessage.objects.create(
            name=self.cleaned_data.get("name", ""),
            email=self.cleaned_data.get("email", ""),
            interest=self.cleaned_data.get("interest", "other"),
            message=self.cleaned_data.get("message", ""),
        )

    def clean_website(self):
        website = self.cleaned_data.get("website", "").strip()
        if website:
            raise forms.ValidationError("Invalid submission.")
        return website

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if any(char.isdigit() for char in name):
            raise forms.ValidationError("Name must not contain numbers.")
        if len(name) < 2:
            raise forms.ValidationError("Please provide your full name.")
        return name

    def clean_message(self):
        message = self.cleaned_data.get("message", "").strip()
        if len(message) < 5:
            raise forms.ValidationError("Please provide a slightly more descriptive message.")
        return message
