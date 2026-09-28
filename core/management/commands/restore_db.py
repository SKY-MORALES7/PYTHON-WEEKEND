import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.core.cache import cache


class Command(BaseCommand):
    help = "Restore website database content from versioned JSON fixture and populate FlatPages."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force restoration even if database tables already contain data.",
        )

    def handle(self, *args, **options):
        force = options.get("force", False)
        base_dir = settings.BASE_DIR
        fixture_file = os.path.join(base_dir, "core", "fixtures", "initial_data.json")

        # 1. Check if database content is empty or if --force is requested
        should_restore = force
        if not should_restore:
            try:
                from content.models import PageContent
                from django.contrib.flatpages.models import FlatPage
                pc_count = PageContent.objects.count()
                fp_count = FlatPage.objects.count()
                if pc_count == 0 or fp_count == 0:
                    should_restore = True
                    self.stdout.write(self.style.NOTICE("Database content missing or empty. Auto-triggering restoration..."))
            except Exception:
                should_restore = True

        if not should_restore:
            self.stdout.write(
                self.style.WARNING(
                    "Database tables already contain data. Skipping restore. "
                    "Use 'python manage.py restore_db --force' to overwrite existing records."
                )
            )
            return

        # 2. Load fixture data if available
        if os.path.exists(fixture_file):
            self.stdout.write(self.style.NOTICE(f"Loading data fixture from {fixture_file}..."))
            try:
                call_command("loaddata", fixture_file)
                self.stdout.write(self.style.SUCCESS("Successfully loaded JSON fixture into database."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error loading fixture: {e}"))

        # 3. Execute populate_flatpages script as safety sync
        script_path = os.path.join(base_dir, "scripts", "populate_flatpages.py")
        if os.path.exists(script_path):
            self.stdout.write(self.style.NOTICE("Syncing FlatPages with frontend templates..."))
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("populate_flatpages", script_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, "run"):
                    module.run()
                self.stdout.write(self.style.SUCCESS("Successfully synced FlatPages."))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Note on FlatPages sync: {e}"))

        # 4. Clear cache
        cache.clear()
        self.stdout.write(self.style.SUCCESS("Django cache cleared successfully!"))
        self.stdout.write(self.style.SUCCESS("Database content restoration complete!"))
