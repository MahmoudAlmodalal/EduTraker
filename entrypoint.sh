#!/bin/sh
set -e

echo "Starting EduTraker Entrypoint..."

DB_REACHABLE="unknown"
DB_CHECK_TIMEOUT_SECONDS="${DB_CHECK_TIMEOUT_SECONDS:-10}"

check_db_connection() {
  if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
    echo "Checking database connection at $DB_HOST:$DB_PORT..."
    if command -v nc >/dev/null 2>&1; then
      if timeout "${DB_CHECK_TIMEOUT_SECONDS}s" nc -z "$DB_HOST" "$DB_PORT"; then
        echo "Database is reachable."
        DB_REACHABLE="true"
      else
        echo "Warning: Could not reach database at $DB_HOST:$DB_PORT."
        DB_REACHABLE="false"
      fi
    else
      echo "netcat not found, skipping direct DB reachability check..."
    fi
  else
    echo "DB_HOST or DB_PORT not set, skipping connection check..."
  fi
}

# Only run migrations if we are likely the backend (not celery) or if explicitly forced
# A simple heuristic: if no arguments are passed, we are the backend starting default gunicorn
if [ $# -eq 0 ]; then
    check_db_connection

    if [ "$DB_REACHABLE" = "false" ]; then
      if [ "${REQUIRE_DB_ON_STARTUP:-False}" = "True" ]; then
        echo "Database is unreachable and REQUIRE_DB_ON_STARTUP=True. Exiting."
        exit 1
      fi
      echo "Skipping db_fix.py and migrations because database is unreachable."
    else
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
    fi

    echo "Collecting static files..."
    python manage.py collectstatic --noinput

    echo "Starting Gunicorn..."
    exec gunicorn --reload --bind 0.0.0.0:8000 --workers 3 --timeout 120 eduTrack.wsgi:application
else
    # If arguments are provided (like for celery), execute them
    echo "Executing provided command: $@"
    exec "$@"
fi
