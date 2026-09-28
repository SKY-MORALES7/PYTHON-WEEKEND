import os
import glob
import shutil
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings


class Command(BaseCommand):
    help = "Backup essential website database content to versioned JSON fixture and timestamped SQLite backup file."

    def handle(self, *args, **options):
        base_dir = settings.BASE_DIR
        
        # 1. Ensure core/fixtures directory exists
        fixtures_dir = os.path.join(base_dir, "core", "fixtures")
        os.makedirs(fixtures_dir, exist_ok=True)
        fixture_file = os.path.join(fixtures_dir, "initial_data.json")

        # 2. Dump essential content models to JSON fixture
        models_to_dump = [
            "content.PageContent",
            "content.WebsiteMenuItem",
            "content.FooterConfig",
            "content.Event",
            "content.EventCoach",
            "content.EventSponsor",
            "flatpages.FlatPage",
            "sites.Site",
            "coach.Coach",
            "sponsors.Sponsor",
            "tutorials.Tutorial",
            "tutorials.TutorialSection",
        ]

        self.stdout.write(self.style.NOTICE("Dumping database content to initial_data.json..."))
        try:
            with open(fixture_file, "w", encoding="utf-8") as f:
                call_command(
                    "dumpdata",
                    *models_to_dump,
                    indent=2,
                    stdout=f,
                    format="json"
                )
            self.stdout.write(self.style.SUCCESS(f"Successfully saved JSON fixture to: {fixture_file}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error dumping fixture data: {e}"))

        # 3. Create timestamped SQLite backup file
        db_path = settings.DATABASES["default"].get("NAME")
        if db_path and os.path.exists(str(db_path)):
            backups_dir = os.path.join(base_dir, "backups")
            os.makedirs(backups_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"db_{timestamp}.sqlite3"
            backup_filepath = os.path.join(backups_dir, backup_filename)
            
            try:
                shutil.copy2(str(db_path), backup_filepath)
                self.stdout.write(self.style.SUCCESS(f"Successfully created database snapshot: {backup_filepath}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error copying database file: {e}"))
                
            # 4. Cleanup old backups (keep top 10 latest)
            backup_files = sorted(glob.glob(os.path.join(backups_dir, "db_*.sqlite3")))
            if len(backup_files) > 10:
                for old_file in backup_files[:-10]:
                    try:
                        os.remove(old_file)
                        self.stdout.write(self.style.NOTICE(f"Cleaned up old backup file: {os.path.basename(old_file)}"))
                    except Exception:
                        pass

        self.stdout.write(self.style.SUCCESS("Database backup completed successfully!"))
