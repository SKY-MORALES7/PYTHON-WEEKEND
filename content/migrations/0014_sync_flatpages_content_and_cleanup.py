from django.db import migrations

def sync_and_clean_flatpages(apps, schema_editor):
    try:
        from scripts.populate_flatpages import run
        run()
    except Exception as e:
        print(f"FlatPages sync migration note: {e}")

def reverse_sync(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('content', '0013_update_footer_copyright_help_text'),
    ]

    operations = [
        migrations.RunPython(sync_and_clean_flatpages, reverse_code=reverse_sync),
    ]
