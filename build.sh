#!/usr/bin/env bash
# exit on error
set -o errexit

npm install
npm run build:css

pip install -r requirements.txt

python manage.py collectstatic --no-input

# --- TEMPORARY DATABASE RESET SCRIPT ---
# We are completely dropping all tables to fix the migration loop
python reset_db.py
# ---------------------------------------

python manage.py migrate
python populate_content.py

