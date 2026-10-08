from django.contrib import admin
from django import forms
from django.contrib.flatpages.admin import FlatPageAdmin as DefaultFlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "interest", "created_at", "read", "replied_status")
    list_filter = ("interest", "read", "created_at")
    search_fields = ("name", "email", "message", "reply")
    readonly_fields = ("created_at", "updated_at", "replied_at")
    fields = (
        "name",
        "email",
        "interest",
        "message",
        "read",
        "reply",
        "replied_at",
        "created_at",
        "updated_at",
    )

    @admin.display(description="Replied", boolean=True)
    def replied_status(self, obj):
        return bool(obj.reply and obj.reply.strip())


class CustomFlatPageForm(forms.ModelForm):
    class Meta:
        model = FlatPage
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        if "content" in self.fields:
            # Adjust spacing in the admin textarea so lines aren't too far apart
            self.fields["content"].widget.attrs.update({"style": "line-height: 1.4; font-family: monospace;"})
            url = getattr(self.instance, "url", "")
            STANDARDIZED_URLS = [
                "/privacy/",
                "/terms/",
                "/about/",
                "/organise/",
                "/organize/",
                "/contribute/",
                "/code-of-conduct/",
                "/coc/",
                "/support/",
                "/support-us/",
                "/partners/",
                "/jobs/",
                "/resources/",
            ]
            if url == "/faq/":
                self.fields["content"].help_text = (
                    "💡 <strong>What to write:</strong> Enter plain text content for the FAQ page. "
                    "Format questions using exactly <strong>Q: Your question?</strong> and "
                    "answers using <strong>A: Your answer text.</strong>"
                )
            elif url in STANDARDIZED_URLS:
                is_superuser = bool(self.request and self.request.user and self.request.user.is_superuser)
                if is_superuser:
                    self.fields["content"].help_text = (
                        "💡 <strong>Notice:</strong> This page's complex layout is hardcoded to ensure it looks beautiful. "
                        "To edit headings or text on this page, please use the <strong>Website Content (PageContent)</strong> app instead of this box."
                    )
                else:
                    self.fields["content"].help_text = (
                        "💡 <strong>Notice:</strong> This page uses a standardized community layout managed by platform leadership. "
                        "If you need custom sections, layout changes, or heading updates on this page, please contact a platform super administrator."
                    )
                    self.fields["content"].disabled = True
                    self.fields["content"].widget.attrs.update({
                        "readonly": "readonly",
                        "style": "line-height: 1.4; font-family: monospace; background-color: #f1f5f9; cursor: not-allowed;",
                    })
            else:
                self.fields["content"].help_text = (
                    "💡 <strong>What to write:</strong> Enter plain text content for this page. "
                    "Use empty lines to separate paragraphs."
                )

    def clean_content(self):
        content = self.cleaned_data.get("content")
        url = getattr(self.instance, "url", "")
        standardized_urls = [
            "/privacy/", "/terms/", "/about/", "/organise/", "/organize/",
            "/contribute/", "/code-of-conduct/", "/coc/", "/support/",
            "/support-us/", "/partners/", "/jobs/", "/resources/",
        ]
        is_superuser = bool(self.request and self.request.user and self.request.user.is_superuser)
        if url in standardized_urls and not is_superuser:
            if self.instance and self.instance.pk:
                return self.instance.content
        return content


class CustomFlatPageAdmin(DefaultFlatPageAdmin):
    form = CustomFlatPageForm
    view_on_site = False

    def get_form(self, request, obj=None, change=False, **kwargs):
        Form = super().get_form(request, obj, change=change, **kwargs)
        class RequestAwareFlatPageForm(Form):
            def __init__(self, *f_args, **f_kwargs):
                f_kwargs["request"] = request
                super().__init__(*f_args, **f_kwargs)
        return RequestAwareFlatPageForm


try:
    admin.site.unregister(FlatPage)
except admin.sites.NotRegistered:
    pass

admin.site.register(FlatPage, CustomFlatPageAdmin)
