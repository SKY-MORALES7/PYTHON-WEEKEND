import os
from django import template
from django.conf import settings

register = template.Library()


@register.filter(name="file_exists")
def file_exists(image_field):
    """
    Returns True only when the ImageField value is set AND the file physically
    exists on disk.  Use this in templates to avoid rendering broken image URLs:

        {% if event.image|file_exists %}
            <img src="{{ event.image.url }}" ...>
        {% else %}
            {# fallback #}
        {% endif %}
    """
    if not image_field:
        return False
    try:
        return os.path.exists(image_field.path)
    except (ValueError, NotImplementedError):
        # path() raises ValueError if the field has no name;
        # some remote storages raise NotImplementedError.
        return False
