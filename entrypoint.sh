#!/bin/sh
set -e

echo "Starting EduTraker Entrypoint..."

if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
  echo "Checking database connection at $DB_HOST:$DB_PORT..."
  # Use netcat if available, otherwise sleep
  if command -v nc >/dev/null 2>&1; then
      if timeout 30s nc -z "$DB_HOST" "$DB_PORT"; then
        echo "Database is reachable."
      else
        echo "Warning: Could not reach database at $DB_HOST:$DB_PORT. Continuing anyway..."
      fi
  else
      echo "netcat not found, sleeping 5s to allow DB startup..."
      sleep 5
  fi
else
  echo "DB_HOST or DB_PORT not set, skipping connection check..."
fi

# Only run migrations if we are likely the backend (not celery) or if explicitly forced
# A simple heuristic: if no arguments are passed, we are the backend starting default gunicorn
if [ $# -eq 0 ]; then
    echo "Running migrations..."
    # Automated Schema Sync Logic
    if [ "$FORCE_MIGRATE_SYNC" = "True" ]; then
      echo "FORCE_MIGRATE_SYNC is True. Re-syncing migration state..."
      python db_fix.py || echo "db_fix.py failed, continuing..."
      python manage.py migrate --fake-initial || echo "Fake initial failed, continuing..."
      python manage.py migrate --noinput
    elif [ "$MIGRATE_FAKE" = "True" ]; then
      echo "Faking migrations..."
      python manage.py migrate --noinput --fake
    else
      echo "Executing standard migration..."
      # Run db reconciliation before migration
      python db_fix.py || echo "db_fix.py failed, continuing..."
      python manage.py migrate --noinput || {
        echo "Migration failed. Attempting to reconcile..."
        python manage.py migrate --fake-initial --noinput || echo "Auto-reconcile failed."
      }
    fi

    echo "Collecting static files..."
    python manage.py collectstatic --noinput

    echo "Starting Gunicorn..."
    exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 eduTrack.wsgi:application
else
    # If arguments are provided (like for celery), execute them
    echo "Executing provided command: $@"
    exec "$@"
fi
