import os
import django
import sys

# Ensure project root is in pythonpath
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pythonweekend.settings")
django.setup()

from tutorials.models import Tutorial
from content.models import WebsiteMenuItem

def run():
    print("Populating missing tutorials for production...")

    # 1. Mentoring Guide
    mentoring_content = """# Mentoring Guide

Good mentoring is central to the Python Weekend experience.

This guide explains how to support beginners, ask useful questions, respond to errors, work with different learning speeds and create a respectful environment without writing participants' projects for them.

## Key Principles
1. **Empathy first**: Remember what it was like when you first learned to code.
2. **Guide, don't do**: Help them find the answer, rather than typing it for them.
3. **Patience**: Everyone learns at their own pace.

*Full guide coming soon...*
"""
    Tutorial.objects.update_or_create(
        slug="mentoring-guide",
        defaults={
            "title": "Mentoring Guide",
            "resource_type": "mentoring_guide",
            "content": mentoring_content,
            "published": True,
            "difficulty": "intermediate"
        }
    )

    # 2. Organiser's Manual
    manual_content = """# Organiser's Manual

A practical handbook containing what local teams need to plan and deliver an official Python Weekend workshop.

## Topics Covered
- **Team Formation**: How to recruit a dedicated team.
- **Budgeting**: Managing expenses and securing sponsorships.
- **Venue Selection**: What makes a good learning environment.
- **Participant Applications**: Selecting a diverse and enthusiastic cohort.
- **Mentor Recruitment**: Finding experienced developers to help.
- **Safety & Code of Conduct**: Ensuring a welcoming space for all.

*Full manual coming soon...*
"""
    Tutorial.objects.update_or_create(
        slug="organisers-manual",
        defaults={
            "title": "Organiser's Manual",
            "resource_type": "organisers_manual",
            "content": manual_content,
            "published": True,
            "difficulty": "intermediate"
        }
    )

    # 3. Tutorial Extensions
    extensions_content = """# Tutorial Extensions

Additional exercises and projects for participants who complete the main tutorial or want to continue learning after the workshop.

Extensions may cover:
- Automation
- Data analysis
- Web applications
- AI APIs
- Responsible AI practice

*New extensions will be added here as they are developed.*
"""
    Tutorial.objects.update_or_create(
        slug="tutorial-extensions",
        defaults={
            "title": "Tutorial Extensions",
            "resource_type": "extension",
            "content": extensions_content,
            "published": True,
            "difficulty": "advanced"
        }
    )

    # 4. Python & AI Tutorial (Parent)
    existing_tutorials = Tutorial.objects.filter(resource_type="workshop_tutorial").exclude(slug="python-ai-tutorial")
    
    links = []
    for t in existing_tutorials:
        links.append(f"- [{t.title}](/resources/{t.slug}/)")
    
    links_md = "\n".join(links)

    tutorial_content = f"""# Python & AI Tutorial

The tutorial used during Python Weekend workshops.

It introduces the learning environment, Python foundations, problem solving, working with simple data and a guided beginner AI project. It is written in plain language and designed for someone learning to program for the first time.

## Chapters

{links_md}
"""
    Tutorial.objects.update_or_create(
        slug="python-ai-tutorial",
        defaults={
            "title": "Python & AI Tutorial",
            "resource_type": "workshop_tutorial",
            "content": tutorial_content,
            "published": True,
            "difficulty": "beginner"
        }
    )

    print("Tutorials populated!")

    # Update Nav Links
    print("Updating WebsiteMenuItem links...")
    WebsiteMenuItem.objects.filter(label__in=['Organiser\'s Manual', 'Mentoring Guide', 'Tutorial Extensions']).delete()
    
    try:
        resources_parent = WebsiteMenuItem.objects.get(label="Resources")
    except WebsiteMenuItem.DoesNotExist:
        resources_parent = WebsiteMenuItem.objects.filter(url="/resources/").first()

    WebsiteMenuItem.objects.update_or_create(
        label="Python & AI Tutorial",
        defaults={"url": "/resources/python-ai-tutorial/", "parent": resources_parent, "order": 1}
    )
    WebsiteMenuItem.objects.update_or_create(
        label="Organiser's Manual",
        defaults={"url": "/resources/organisers-manual/", "parent": resources_parent, "order": 2}
    )
    WebsiteMenuItem.objects.update_or_create(
        label="Mentoring Guide",
        defaults={"url": "/resources/mentoring-guide/", "parent": resources_parent, "order": 3}
    )
    WebsiteMenuItem.objects.update_or_create(
        label="Tutorial Extensions",
        defaults={"url": "/resources/tutorial-extensions/", "parent": resources_parent, "order": 4}
    )
    print("Nav links updated!")

if __name__ == "__main__":
    run()
