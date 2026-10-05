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


from django.utils.safestring import mark_safe

class CodeMirrorWidget(forms.Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        id_ = attrs.get('id', f'id_{name}')
        script = f"""
        <script>
        (function() {{
            function init() {{
                if (typeof CodeMirror === 'undefined') {{
                    setTimeout(init, 100);
                    return;
                }}
                var el = document.getElementById('{id_}');
                if (el && !el.nextElementSibling?.classList?.contains('CodeMirror')) {{
                    var cm = CodeMirror.fromTextArea(el, {{
                        mode: 'htmlmixed',
                        theme: 'monokai',
                        lineNumbers: true,
                        lineWrapping: true,
                        viewportMargin: Infinity
                    }});
                }}
            }}
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', init);
            }} else {{
                init();
            }}
        }})();
        </script>
        <style>
        .CodeMirror {{ height: auto; min-height: 400px; border: 1px solid #333; border-radius: 4px; font-size: 14px; font-family: 'JetBrains Mono', monospace; }}
        </style>
        """
        return mark_safe(html + script)


class CustomFlatPageForm(forms.ModelForm):
    class Meta:
        model = FlatPage
        fields = "__all__"
        widgets = {
            'content': CodeMirrorWidget()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "content" in self.fields:
            url = getattr(self.instance, "url", "")
            if url == "/faq/":
                self.fields["content"].help_text = (
                    "💡 <strong>What to write:</strong> Enter plain text content for the FAQ page. "
                    "Format questions using exactly <strong>Q: Your question?</strong> and "
                    "answers using <strong>A: Your answer text.</strong>"
                )
            elif url in ["/support/", "/support-us/", "/partners/"]:
                self.fields["content"].help_text = (
                    "💡 <strong>Notice:</strong> This page's complex layout and dynamic sponsor lists are hardcoded. "
                    "You cannot edit the main layout here."
                )
            else:
                self.fields["content"].help_text = (
                    "💡 <strong>What to write:</strong> You can edit the text inside the HTML tags here. "
                    "The color-coding helps you distinguish between tags (pink/blue) and text (white/yellow)."
                )


class CustomFlatPageAdmin(DefaultFlatPageAdmin):
    form = CustomFlatPageForm
    view_on_site = False

    class Media:
        css = {
            'all': (
                'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.min.css',
                'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/theme/monokai.min.css',
            )
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/mode/xml/xml.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/mode/htmlmixed/htmlmixed.min.js',
        )


try:
    admin.site.unregister(FlatPage)
except admin.sites.NotRegistered:
    pass

admin.site.register(FlatPage, CustomFlatPageAdmin)
