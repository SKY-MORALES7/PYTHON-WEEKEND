import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pythonweekend.settings')
django.setup()

if connection.vendor == 'postgresql':
    with connection.cursor() as cursor:
        cursor.execute("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
            END $$;
        """)
    print("All Postgres tables dropped successfully.")
elif connection.vendor == 'sqlite':
    # Don't drop sqlite tables automatically just to be safe for local dev
    print("SQLite database detected. Skipping automatic table drop.")
