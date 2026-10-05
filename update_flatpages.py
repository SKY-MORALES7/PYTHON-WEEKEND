import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pythonweekend.settings')
django.setup()

from django.contrib.flatpages.models import FlatPage
from django.utils.html import strip_tags
import re

for fp in FlatPage.objects.all():
    if fp.content:
        # Strip HTML tags but preserve some spacing
        text = fp.content.replace('</p>', '\n\n').replace('<br>', '\n').replace('</div>', '\n\n')
        text = strip_tags(text)
        # Clean up excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text).strip()
        fp.content = text
        fp.save()
        print(f"Updated {fp.url}")
