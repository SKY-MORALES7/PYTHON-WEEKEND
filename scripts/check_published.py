import os
import sys
import django

# Ensure project root is on sys.path so Django settings module can be imported
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pythonweekend.settings')
django.setup()

from content.models import BlogPost, Tutorial, Event

models = [
    ('BlogPost', BlogPost),
    ('Tutorial', Tutorial),
    ('Event', Event),
]

for name, model in models:
    total = model.objects.count()
    published = model.objects.filter(published=True).count()
    print(f"{name}: total={total}, published={published}")
