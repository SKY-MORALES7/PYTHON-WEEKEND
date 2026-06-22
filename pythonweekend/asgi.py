"""
ASGI config for Python Weekend project.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pythonweekend.settings")

application = get_asgi_application()
