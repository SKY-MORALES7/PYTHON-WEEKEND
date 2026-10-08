from django.db import migrations

TERMS_CONTENT = """Terms and Conditions

Please read these terms and conditions carefully before using pythonweekend.org.

By accessing and using this website, you agree to comply with and be bound by the following terms and conditions of use:

1. Ownership and Operation

pythonweekend.org is owned and operated by Code Campus International. All contents, graphics, and materials associated with Python Weekend are protected under applicable intellectual property laws.

2. Event Applications and Participant Selection

Applications for Python Weekend workshops are submitted through official channels. Submission of an application does not guarantee acceptance or a confirmed workshop seat.

3. Use of Learning Materials

The Python Weekend learning resources, tutorials, and organiser manuals are provided for educational and community use under approved licensing terms.

4. Code of Conduct

All participants, organisers, mentors, and visitors must adhere to the official Python Weekend Code of Conduct across all physical and digital spaces.

5. Availability of the Site

We do not guarantee that pythonweekend.org or its services will be available uninterrupted or error-free at all times. If the site is unavailable, suspended, or interrupted for any reason, we cannot be held responsible or liable for any loss, delay, or damage incurred as a result.

We reserve the right to modify, update, suspend, or discontinue any aspect of the site or the services offered at any time without prior notice.

6. Changes and Contact Information

We reserve the right to update these terms at any time. For questions regarding terms and conditions, contact us at hello@pythonweekend.org."""

def update_terms_content(apps, schema_editor):
    FlatPage = apps.get_model("flatpages", "FlatPage")
    flatpage = FlatPage.objects.filter(url="/terms/").first()
    if flatpage:
        flatpage.content = TERMS_CONTENT
        flatpage.save()

class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_contactmessage_replied_at_contactmessage_reply"),
        ("flatpages", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(update_terms_content, migrations.RunPython.noop),
    ]
