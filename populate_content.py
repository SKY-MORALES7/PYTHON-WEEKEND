import os
import re
import django
from django.utils import timezone
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pythonweekend.settings')
django.setup()

from django.contrib.sites.models import Site
from django.contrib.flatpages.models import FlatPage
from content.models import Event
from django.contrib.auth.models import User

def populate():
    # Setup Site
    site, _ = Site.objects.get_or_create(id=1)
    site.domain = 'pythonweekend.com'
    site.name = 'Python Weekend'
    site.save()
    
    # Read markdown
    md_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pythonweekend', 'Python_Weekend_Website_Content.md')
    if not os.path.exists(md_path):
        print("Markdown file not found.")
        return
        
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Split by major headings: "# [Number]. "
    sections = re.split(r'\n# \d+\.\s+', content)
    
    # Map section titles to URLs
    pages_to_create = {
        'Support a Workshop Page': ('/support-us/', 'Support a Workshop'),
        'Our Partners Page': ('/partners/', 'Our Partners'),
        'Organise a Workshop Page': ('/organise/', 'Organise a Workshop'),
        'Contribute Page': ('/contribute/', 'Contribute'),
        'Resources Page': ('/resources/', 'Resources'),
        'Newsletter Page': ('/newsletter/', 'Newsletter'),
        'Frequently Asked Questions Page': ('/faq/', 'Frequently Asked Questions'),
    }
    
    for section in sections[1:]: # Skip the first chunk (intro)
        lines = section.split('\n', 1)
        if len(lines) < 2: continue
        title_line = lines[0].strip()
        body = lines[1].strip()
        
        if title_line in pages_to_create:
            url, title = pages_to_create[title_line]
            fp, created = FlatPage.objects.get_or_create(url=url, defaults={'title': title})
            fp.content = body
            fp.title = title
            fp.save()
            fp.sites.add(site)
            print(f"Updated FlatPage: {title} ({url})")

    # Create the Abuja Event
    user, _ = User.objects.get_or_create(username="admin", defaults={'is_superuser': True, 'is_staff': True, 'email': 'admin@example.com', 'password': 'admin'})
    event, created = Event.objects.get_or_create(
        slug="abuja-2025",
        defaults={
            'title': 'Python Weekend Abuja',
            'tagline': 'Build Your First Python Project With AI!',
            'start_date': timezone.make_aware(datetime(2025, 2, 21, 9, 0)),
            'end_date': timezone.make_aware(datetime(2025, 2, 22, 17, 0)),
            'location': 'To be announced',
            'city': 'Abuja',
            'description': 'Python Weekend Abuja is bringing complete beginners together for a free, practical weekend of learning.',
            'published': True,
            'owner': user
        }
    )
    if not created:
        event.title = 'Python Weekend Abuja'
        event.tagline = 'Build Your First Python Project With AI!'
        event.description = 'Python Weekend Abuja is bringing complete beginners together for a free, practical weekend of learning.'
        event.published = True
        event.save()
    print("Updated Event: Python Weekend Abuja")

if __name__ == '__main__':
    populate()
