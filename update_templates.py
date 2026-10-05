import os

TEMPLATE_DIR = r"c:\Users\dooli\OneDrive\Desktop\PYTHON-WEEKEND\templates\core"

templates_to_update = [
    "about.html",
    "coc.html",
    "contribute.html",
    "jobs.html",
    "organise.html",
    "partners.html",
    "resources.html",
    "support.html",
]

base_content = """{% extends "base.html" %}
{% load content_tags %}

{% block title %}{{ flatpage.title }} - Python Weekend{% endblock %}

{% block content %}
{{ flatpage.content|safe }}
{% endblock %}
"""

for t in templates_to_update:
    path = os.path.join(TEMPLATE_DIR, t)
    if os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(base_content)
        print(f"Updated {t}")
    else:
        print(f"Not found: {t}")
