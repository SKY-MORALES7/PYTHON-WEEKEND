#!/usr/bin/env bash
# exit on error
set -o errexit

npm install
npm run build:css

pip install -r requirements.txt

python manage.py collectstatic --no-input

# --- TEMPORARY DATABASE RESET SCRIPT ---
# Disabled to prevent wiping database tables on deployment
# python reset_db.py
# ---------------------------------------

python manage.py migrate
python manage.py restore_db
python scripts/update_resource_menus.py

