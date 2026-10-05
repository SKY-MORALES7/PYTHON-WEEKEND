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
            # Adjust spacing in the admin textarea so lines aren't too far apart
            self.fields["content"].widget.attrs.update({"style": "line-height: 1.4; font-family: monospace;"})
            url = getattr(self.instance, "url", "")
            if url == "/faq/":
                self.fields["content"].help_text = (
                    "💡 <strong>What to write:</strong> Enter plain text content for the FAQ page. "
                    "Format questions using exactly <strong>Q: Your question?</strong> and "
                    "answers using <strong>A: Your answer text.</strong>"
                )
            elif url in ["/about/", "/organise/", "/organize/", "/contribute/", "/code-of-conduct/", "/coc/", "/support/", "/support-us/", "/partners/", "/jobs/", "/resources/"]:
                self.fields["content"].help_text = (
                    "⚠️ <strong>Warning:</strong> This page uses complex HTML to render its layout. "
                    "You CAN edit the text here, but <strong>do not delete or change the HTML tags</strong> "
                    "(&lt;div&gt;, &lt;p&gt;, &lt;h2&gt;, etc.) or you will break the page's design!"
                )
            else:
                self.fields["content"].help_text = (
                    "💡 <strong>What to write:</strong> Enter plain text content for this page. "
                    "Use empty lines to separate paragraphs."
                )


class CustomFlatPageAdmin(DefaultFlatPageAdmin):
    form = CustomFlatPageForm
    view_on_site = False


try:
    admin.site.unregister(FlatPage)
except admin.sites.NotRegistered:
    pass

admin.site.register(FlatPage, CustomFlatPageAdmin)
