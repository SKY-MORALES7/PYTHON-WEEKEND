from django.contrib import admin
from django import forms
from django.contrib.flatpages.admin import FlatPageAdmin as DefaultFlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
	list_display = ("name", "email", "interest", "created_at", "read")
	list_filter = ("interest", "read", "created_at")
	search_fields = ("name", "email", "message")
	readonly_fields = ("created_at", "updated_at")


class CustomFlatPageForm(forms.ModelForm):
    class Meta:
        model = FlatPage
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "content" in self.fields:
            url = getattr(self.instance, "url", "")
            if url == "/faq/":
                self.fields["content"].help_text = (
                    "💡 <strong>What to write:</strong> Enter HTML content for the FAQ page. "
                    "Format questions using <code>&lt;h3&gt;Q: Your question?&lt;/h3&gt;</code> and "
                    "answers using <code>&lt;p&gt;A: Your answer text.&lt;/p&gt;</code>."
                )
            elif url == "/about/":
                self.fields["content"].help_text = (
                    "💡 <strong>What to write:</strong> Enter HTML content for the About page. "
                    "Use <code>&lt;h2&gt;</code> for section headers, <code>&lt;p&gt;</code> for paragraphs, "
                    "and <code>&lt;ul&gt;&lt;li&gt;</code> for bulleted lists."
                )
            elif url in ["/code-of-conduct/", "/coc/"]:
                self.fields["content"].help_text = (
                    "💡 <strong>What to write:</strong> Enter HTML content for Code of Conduct. "
                    "Use <code>&lt;h2&gt;</code> for section headings and <code>&lt;ul&gt;&lt;li&gt;</code> for conduct rules."
                )
            elif url in ["/support/", "/support-us/"]:
                self.fields["content"].help_text = (
                    "💡 <strong>What to write:</strong> Enter HTML content for the Support page. "
                    "Describe your mission, sponsorship tracks, and how partners can contribute."
                )
            elif url == "/partners/":
                self.fields["content"].help_text = (
                    "💡 <strong>What to write:</strong> Enter HTML content for Our Partners. "
                    "Describe partnership tiers and how organisations can partner with Python Weekend."
                )
            elif url in ["/organise/", "/organize/"]:
                self.fields["content"].help_text = (
                    "💡 <strong>What to write:</strong> Enter HTML content for the Organise page. "
                    "Explain requirements for hosting in-person and remote workshops."
                )
            elif url == "/contribute/":
                self.fields["content"].help_text = (
                    "💡 <strong>What to write:</strong> Enter HTML content for the Contribute page. "
                    "Outline how volunteers can mentor, organize, write tutorials, or support."
                )
            elif url == "/resources/":
                self.fields["content"].help_text = (
                    "💡 <strong>What to write:</strong> Enter HTML content for Resources. "
                    "Detail the tutorial, organiser manual, mentoring guide, and extensions."
                )
            else:
                self.fields["content"].help_text = (
                    "💡 <strong>What to write:</strong> Enter HTML or rich text content for this page. "
                    "Supported HTML tags: &lt;h1&gt;, &lt;h2&gt;, &lt;h3&gt;, &lt;p&gt;, &lt;ul&gt;, &lt;li&gt;, &lt;strong&gt;, &lt;a&gt;."
                )


class CustomFlatPageAdmin(DefaultFlatPageAdmin):
    form = CustomFlatPageForm


try:
    admin.site.unregister(FlatPage)
except admin.sites.NotRegistered:
    pass

admin.site.register(FlatPage, CustomFlatPageAdmin)
