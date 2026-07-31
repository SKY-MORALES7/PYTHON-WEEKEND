import os
import django
import sys
from datetime import datetime
from django.utils.text import slugify

# Setup Django environment
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pythonweekend.settings")
django.setup()

from content.models import Event, Tutorial, BlogPost
from sponsors.models import Sponsor
from coach.models import Coach

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
            "description": "Are you curious about Python and artificial intelligence but do not know where to begin? We have good news for you.\n\nPython Weekend Abuja is bringing complete beginners together for a free, practical weekend of learning. You will learn the foundations of Python, explore how Python is used in AI and build a small guided project with support from friendly mentors.\n\nOur goal is to help you move from curiosity to working code and leave with the confidence to continue learning.",
            "day1_title": "Day One: Python Foundations",
            "day1_schedule": "09:00 — Doors open and participant check in\n09:30 — Welcome and introduction to Python Weekend\n10:00 — Laptop setup and installation support\n11:00 — Python foundations: variables, data types, input and output\n13:00 — Break\n14:00 — Conditions, loops and functions\n15:30 — Guided exercises and mentor support\n17:30 — Day one wrap up",
            "day2_title": "Day Two: Build With AI",
            "day2_schedule": "09:00 — Doors open and recap\n09:30 — Working with simple data in Python\n11:00 — Understanding AI, machine learning and generative AI\n12:00 — Responsible AI: privacy, accuracy, bias and human judgement\n13:00 — Break\n14:00 — Guided Python and AI project\n16:00 — Project sharing and next learning steps\n17:30 — Official close",
            "what_you_learn": "Python foundations\nVariables, conditions, loops\nBeginner AI concepts\nGenerative AI APIs\nWorking with simple data",
            "who_should_apply": "Complete beginners\nPeople with no programming experience\nCurious individuals eager to learn",
            "faq": "Q: Do I need to know Python, AI or programming?\nA: No. The workshop is designed for complete beginners. You do not need previous programming experience.\n\nQ: Do I need to bring a laptop?\nA: Yes. Bring a working laptop and charger.",
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
            "content": "This tutorial introduces the learning environment, Python foundations, problem solving, working with simple data and a guided beginner AI project. It is written in plain language and designed for someone learning to program for the first time.",
            "difficulty": "beginner",
            "estimated_minutes": 480,
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
            "content": "That first workshop created a welcoming starting point for people who wanted to learn Python in a practical community setting.\n\nWith every new edition, we aim to help more beginners write their first lines of Python, understand the foundations of AI and discover a clearer path for continued learning.",
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
            "tagline": "Parent organization of Python Weekend",
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
            "bio": "Experienced organiser shaping Python Weekend to deliver patient mentorship, accessible learning and community led delivery.",
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
