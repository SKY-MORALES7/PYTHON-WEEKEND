import os
from django import template
from django.conf import settings

register = template.Library()


@register.filter(name="file_exists")
def file_exists(image_field):
    """
    Returns True when the ImageField value is set.
    For local storage, verifies physical existence on disk.
    For remote storage (Cloudinary, S3), path() raises NotImplementedError,
    so we return True if image_field.name is present.
    """
    if not image_field or not getattr(image_field, "name", None):
        return False

    try:
        if hasattr(image_field, "path"):
            return os.path.exists(image_field.path)
    except (ValueError, NotImplementedError, AttributeError):
        pass

    return bool(image_field.name)

