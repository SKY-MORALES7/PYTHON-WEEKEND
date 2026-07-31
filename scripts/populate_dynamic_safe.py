import os
import django
import sys
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pythonweekend.settings")
django.setup()

from django.apps import apps
from sponsors.models import Sponsor
from coach.models import Coach

# Find models dynamically to avoid ImportError
try:
    Event = apps.get_model('content', 'Event')
except LookupError:
    try:
        Event = apps.get_model('core', 'Event')
    except LookupError:
        print("Could not find Event model anywhere!")
        sys.exit(1)

try:
    Tutorial = apps.get_model('content', 'Tutorial')
    BlogPost = apps.get_model('content', 'BlogPost')
except LookupError:
    print("Could not find Tutorial or BlogPost models!")
    sys.exit(1)

def run():
    print("Populating specific models based on Python Weekend Website Content...")
    
    # 1. Create an Event
    event, created = Event.objects.get_or_create(
        slug="python-weekend-abuja-2025",
        defaults={
            "title": "Python Weekend Abuja",
            "tagline": "Build Your First Python Project With AI!",
            "start_date": datetime(2025, 2, 21, 9, 0),
            "end_date": datetime(2025, 2, 22, 18, 0),
            "location": "Abuja, Nigeria",
            "venue_name": "Code Campus International Hub",
            "city": "Abuja",
            "description": "Are you curious about Python and artificial intelligence but do not know where to begin? We have good news for you.\n\nPython Weekend Abuja is bringing complete beginners together for a free, practical weekend of learning.",
            "what_you_learn": "Python foundations\nVariables, conditions, loops",
            "who_should_apply": "Complete beginners",
            "published": True
        }
    )
    if created:
        print("Created Event: Python Weekend Abuja")
    else:
        print("Event 'Python Weekend Abuja' already exists")

    # 2. Create a Tutorial
    tutorial, created = Tutorial.objects.get_or_create(
        slug="python-and-ai-tutorial",
        defaults={
            "title": "Python and AI Tutorial",
            "excerpt": "The official tutorial used during Python Weekend workshops.",
            "difficulty": "beginner",
            "published": True
        }
    )
    if created:
        print("Created Tutorial: Python and AI Tutorial")
    else:
        print("Tutorial 'Python and AI Tutorial' already exists")

    # 3. Create a Blog Post
    blog, created = BlogPost.objects.get_or_create(
        slug="first-python-weekend-abuja",
        defaults={
            "title": "Our First Python Weekend in Abuja",
            "excerpt": "Python Weekend began in Abuja with its first edition on 21 and 22 February 2025.",
            "author": "Code Campus International",
            "published": True,
            "published_at": datetime.now()
        }
    )
    if created:
        print("Created Blog Post: Our First Python Weekend in Abuja")
    else:
        print("Blog Post already exists")

    # 4. Create a Sponsor
    sponsor, created = Sponsor.objects.get_or_create(
        name="Code Campus International",
        defaults={
            "website": "https://pythonweekend.org",
            "tier": "platinum",
            "active": True
        }
    )
    if created:
        print("Created Sponsor: Code Campus International")
    else:
        print("Sponsor already exists")

    # 5. Create a Coach/Mentor
    coach, created = Coach.objects.get_or_create(
        name="Mayokun Adeoti",
        defaults={
            "role": "Lead Mentor / Organiser",
            "active": True
        }
    )
    if created:
        print("Created Coach: Mayokun Adeoti")
    else:
        print("Coach already exists")

    print("\nDynamic content successfully populated! You can now check your Admin panel.")

if __name__ == "__main__":
    run()
