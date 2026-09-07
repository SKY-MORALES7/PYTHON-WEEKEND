import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pythonweekend.settings")
django.setup()

from content.models import WebsiteMenuItem
from django.core.cache import cache

def run():
    print("Updating Resource Menu Items in Database...")

    # Header menu items under Resources
    resources_parent = WebsiteMenuItem.objects.filter(label="Resources", position="header").first()
    
    resource_links = [
        ("Python & AI Tutorial", "/resources/python-ai-tutorial/"),
        ("Organiser's Manual", "/resources/organisers-manual/"),
        ("Mentoring Guide", "/resources/mentoring-guide/"),
        ("Tutorial Extensions", "/resources/tutorial-extensions/"),
    ]

    for order, (label, url) in enumerate(resource_links, start=1):
        # Update or create in header
        if resources_parent:
            item, created = WebsiteMenuItem.objects.update_or_create(
                position="header",
                label=label,
                defaults={
                    "url": url,
                    "parent": resources_parent,
                    "order": order,
                    "is_active": True,
                }
            )
            print(f"Header: {label} -> {url} ({'created' if created else 'updated'})")

        # Update in footer (under 'Resources' column)
        footer_item = WebsiteMenuItem.objects.filter(position="footer", label=label).first()
        if footer_item:
            footer_item.url = url
            footer_item.footer_column = "Resources"
            footer_item.order = order
            footer_item.is_active = True
            footer_item.save()
            print(f"Footer: {label} -> {url} (updated)")
        else:
            WebsiteMenuItem.objects.create(
                position="footer",
                label=label,
                url=url,
                footer_column="Resources",
                order=order,
                is_active=True,
            )
            print(f"Footer: {label} -> {url} (created)")

    # Clear site menus cache
    cache.delete("site_menu_header")
    cache.delete("site_menu_footer")
    print("Menu cache cleared successfully!")

if __name__ == "__main__":
    run()
