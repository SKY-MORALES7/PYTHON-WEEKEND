import os
import django
from django.utils.text import slugify
from django.utils import timezone
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pythonweekend.settings')
django.setup()

from content.models import Event, Tutorial, TutorialSection, BlogPost, BlogSection
from sponsors.models import Sponsor
from coach.models import Coach
from django.contrib.auth.models import User

def populate():
    print("Populating database with content from Python_Weekend_Website_Content.md...")

    # Create a superuser if we need an owner for the event
    user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com'})
    if created:
        user.set_password('admin')
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print("Created superuser 'admin'")

    # 1. Populating Event
    event_title = "Python Weekend Abuja"
    event, event_created = Event.objects.get_or_create(
        slug=slugify(event_title),
        defaults={
            'title': event_title,
            'tagline': "Free Python and AI Workshop for Beginners",
            'start_date': timezone.make_aware(datetime(2025, 2, 21, 9, 0)),
            'end_date': timezone.make_aware(datetime(2025, 2, 22, 17, 0)),
            'location': "Abuja, Nigeria",
            'city': "Abuja",
            'description': "Are you curious about Python and artificial intelligence but do not know where to begin? We have good news for you.\n\nPython Weekend Abuja is bringing complete beginners together for a free, practical weekend of learning. You will learn the foundations of Python, explore how Python is used in AI and build a small guided project with support from friendly mentors.\n\nOur goal is to help you move from curiosity to working code and leave with the confidence to continue learning.",
            
            'day1_title': "Python Foundations",
            'day1_schedule': """09:00 — Doors open and participant check in
09:30 — Welcome and introduction to Python Weekend
10:00 — Laptop setup and installation support
11:00 — Python foundations: variables, data types, input and output
13:00 — Break
14:00 — Conditions, loops and functions
16:00 — Guided exercises and mentor support
18:00 — Day one wrap up""",
            
            'day2_title': "Build With AI",
            'day2_schedule': """09:00 — Doors open and recap
09:30 — Working with simple data in Python
11:00 — Understanding AI, machine learning and generative AI
12:30 — Responsible AI: privacy, accuracy, bias and human judgement
13:00 — Break
14:00 — Guided Python and AI project
16:00 — Project sharing and next learning steps
17:00 — Official close""",
            
            'what_you_learn': """Python foundations
Problem solving
Working with simple data
Generative AI
Responsible AI""",
            
            'who_should_apply': """Complete beginners
People with no previous programming experience
Curious minds wanting to learn AI""",
            
            'faq': """Q: Do I need to know Python, AI or programming?
A: No. The workshop is designed for complete beginners. You do not need previous programming experience.

Q: Can I apply if I do not live in Abuja?
A: Yes, unless the local team has stated a location requirement. You will be responsible for your own travel and accommodation unless the event page says otherwise.

Q: Do I need to bring a laptop?
A: Yes. Bring a working laptop and charger. If the local edition has limited device support, the organisers will explain how to request it.

Q: Do I need to install anything before the workshop?
A: Selected participants will receive preparation instructions. The local team may also provide installation support before or at the beginning of the event.

Q: Will food be provided?
A: The local team will state whether meals or refreshments are included.

Q: Is there any cost?
A: Official Python Weekend workshops are free to selected participants. The local team will never request an unofficial payment to confirm a place.

Q: Is Python Weekend only for women?
A: No. Python Weekend welcomes beginners of all genders. We are committed to inclusion and intentionally encourage women and people who have had limited access to technology education to apply.""",
            
            'application_deadline': datetime(2025, 2, 1, 23, 59).date(),
            'application_open': True,
            'published': True,
            'owner': user
        }
    )
    if event_created:
        print(f"Created Event: {event_title}")
    else:
        print(f"Event already exists: {event_title}")

    # 2. Populating Tutorial
    tutorial_title = "Python and AI Tutorial"
    tutorial, tut_created = Tutorial.objects.get_or_create(
        slug=slugify(tutorial_title),
        defaults={
            'title': tutorial_title,
            'excerpt': "The tutorial used during Python Weekend workshops. It introduces the learning environment, Python foundations, problem solving, working with simple data and a guided beginner AI project.",
            'content': "This is the official tutorial for Python Weekend. It is designed for someone learning to program for the first time.",
            'difficulty': "beginner",
            'estimated_minutes': 480, # 8 hours
            'published': True
        }
    )
    if tut_created:
        print(f"Created Tutorial: {tutorial_title}")
        
        # Add some sections to the tutorial
        TutorialSection.objects.create(
            tutorial=tutorial,
            order=1,
            heading="1. Installation",
            body="First, we need to install Python on your machine. We will guide you through the process for Windows, macOS, and Linux."
        )
        TutorialSection.objects.create(
            tutorial=tutorial,
            order=2,
            heading="2. Your First Python Program",
            body="Let's write your first Python program. Open your text editor and type the following:",
            code_block='print("Hello, Python Weekend!")',
            language="python"
        )
    else:
        print(f"Tutorial already exists: {tutorial_title}")

    # 3. Populating BlogPost
    blog_title = "Welcome to Python Weekend!"
    blog, blog_created = BlogPost.objects.get_or_create(
        slug=slugify(blog_title),
        defaults={
            'title': blog_title,
            'excerpt': "Python Weekend began in Abuja with its first edition on 21 and 22 February 2025. That first workshop created a welcoming starting point.",
            'author': "Python Weekend Team",
            'published': True,
            'published_at': timezone.now()
        }
    )
    if blog_created:
        print(f"Created BlogPost: {blog_title}")
        BlogSection.objects.create(
            post=blog,
            order=1,
            heading="Our Mission",
            body="Python Weekend helps complete beginners learn Python and take their first practical step into artificial intelligence through free, mentor supported workshops.\n\nWe support local volunteer teams with a shared programme framework, organiser guidance, learning resources and central coordination."
        )
    else:
        print(f"BlogPost already exists: {blog_title}")

    # 4. Populating Sponsor
    sponsor_name = "Code Campus International"
    sponsor, spon_created = Sponsor.objects.get_or_create(
        name=sponsor_name,
        defaults={
            'website': "https://example.com",
            'tagline': "An initiative of Code Campus International.",
            'tier': "platinum",
            'active': True
        }
    )
    if spon_created:
        print(f"Created Sponsor: {sponsor_name}")
    else:
        print(f"Sponsor already exists: {sponsor_name}")

    print("Database population completed successfully!")

if __name__ == "__main__":
    populate()
