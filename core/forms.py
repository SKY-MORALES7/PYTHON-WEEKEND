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

    # ── Invisible honeypot traps & signed timestamp for bots ──────────────────
    # Avoid `display:none` on the input itself because headless bots scan for it
    # and skip filling it. Instead, hide via off-screen container in template.
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "tabindex": "-1",
            "autocomplete": "new-password",
            "placeholder": "https://yourwebsite.com",
        }),
    )
    company_url = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "tabindex": "-1",
            "autocomplete": "new-password",
            "placeholder": "Company website",
        }),
    )
    form_ts = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            from .security import generate_form_timestamp
            self.fields["form_ts"].initial = generate_form_timestamp()

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

    def clean_company_url(self):
        company_url = self.cleaned_data.get("company_url", "").strip()
        if company_url:
            raise forms.ValidationError("Invalid submission.")
        return company_url

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if any(char.isdigit() for char in name):
            raise forms.ValidationError("Name must not contain numbers.")
        if len(name) < 2:
            raise forms.ValidationError("Please provide your full name.")
        if "http://" in name.lower() or "https://" in name.lower() or "www." in name.lower():
            raise forms.ValidationError("Name must not contain URLs.")

        # Detect single-word CamelCase bot names (e.g., "RobertRuche", "WilliamPhali", "FaustoBex")
        if " " not in name and re.search(r"[a-z]+[A-Z][a-z]+", name):
            raise forms.ValidationError("Please enter your full name with a space between first and last name.")

        # Exact match for known spam bot signatures
        normalized_name = "".join(name.lower().split())
        if normalized_name in ("robertruche", "robertruches", "williamphali", "fausto"):
            raise forms.ValidationError("Invalid submission.")
        return name

    def clean_message(self):
        message = self.cleaned_data.get("message", "").strip()
        if len(message) < 10 or len(message.split()) < 2:
            raise forms.ValidationError("Please provide a slightly more descriptive message (at least a few words).")
        return message
