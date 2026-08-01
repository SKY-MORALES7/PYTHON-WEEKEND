import os
import django
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pythonweekend.settings")
django.setup()

try:
    from content.models import Event
    print("Event imported successfully from content.models")
except Exception as e:
    import traceback
    traceback.print_exc()
