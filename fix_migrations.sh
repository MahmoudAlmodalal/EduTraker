#!/bin/bash
# This script is designed to resolve the "Table already exists" error on Render.
# It fakes the initial migration for the teacher app which is causing the conflict.

echo "Starting migration fix..."

# Ensure we are in the project root
cd "$(dirname "$0")"

# Fake the teacher 0001 migration
echo "Faking teacher.0001_initial migration..."
python manage.py migrate --fake teacher 0001

# Run the rest of the migrations normally
echo "Running remaining migrations..."
python manage.py migrate

echo "Migration fix completed."
