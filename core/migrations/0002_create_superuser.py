from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_superuser(apps, schema_editor):
    # Dynamically get the User model from the auth app
    User = apps.get_model('auth', 'User')
    
    # Check if the user already exists to avoid errors on multiple runs
    if not User.objects.filter(username='render').exists():
        User.objects.create(
            username='render',
            password=make_password('admin123'),
            is_superuser=True,
            is_staff=True,
            is_active=True
        )

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
