from django.db import migrations

def update_help_text(apps, schema_editor):
    PageContent = apps.get_model('content', 'PageContent')
    try:
        content = PageContent.objects.get(key='footer_copyright')
        content.admin_help_text = (
            "Copyright line shown at the very bottom of every page. Use {year} as a placeholder "
            "for the current year. (Note: The words 'Code Campus' will automatically be turned into a link "
            "using the Footer — Code Campus URL setting.)"
        )
        content.save()
    except PageContent.DoesNotExist:
        pass

class Migration(migrations.Migration):

    dependencies = [
        ('content', '0012_add_code_campus_url_page_content'),
    ]

    operations = [
        migrations.RunPython(update_help_text, reverse_code=migrations.RunPython.noop),
    ]
