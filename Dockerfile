FROM python:3.10-slim

# Prevent Python from writing .pyc files and buffer logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies for MySQL client, healthchecks, and CA certificates
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    netcat-openbsd \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy project files
COPY . .

# Create an entrypoint script to handle migrations and wait for DB
RUN echo '#!/bin/sh\n\
set -e\n\
\n\
echo "Starting EduTraker Automated Entrypoint..."\n\
\n\
if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then\n\
  echo "Checking database connection at $DB_HOST:$DB_PORT..."\n\
  if timeout 30s nc -z "$DB_HOST" "$DB_PORT"; then\n\
    echo "Database is reachable."\n\
  else\n\
    echo "Warning: Could not reach database at $DB_HOST:$DB_PORT. Continuing anyway..."\n\
  fi\n\
else\n\
  echo "DB_HOST or DB_PORT not set, skipping connection check..."\n\
fi\n\
\n\
echo "Running migrations..."\n\
# Automated Schema Sync Logic\n\
if [ "$FORCE_MIGRATE_SYNC" = "True" ]; then\n\
  echo "FORCE_MIGRATE_SYNC is True. Re-syncing migration state..."\n\
  python manage.py migrate --fake-initial || echo "Fake initial failed, continuing..."\n\
  python manage.py migrate --noinput\n\
elif [ "$MIGRATE_FAKE" = "True" ]; then\n\
  echo "Faking migrations..."\n\
  python manage.py migrate --noinput --fake\n\
else\n\
  echo "Executing standard migration..."\n\
  # Try standard migrate, if it fails due to schema mismatch, attempt to show status\n\
  python manage.py migrate --noinput || {\n\
    echo "Migration failed. This usually means the DB schema is out of sync with migration files."\n\
    echo "Attempting to reconcile by faking existing migrations..."\n\
    python manage.py migrate --fake-initial --noinput || echo "Auto-reconcile failed."\n\
    python manage.py showmigrations\n\
  }\n\
fi\n\
\n\
echo "Collecting static files..."\n\
python manage.py collectstatic --noinput\n\
\n\
echo "Starting Gunicorn..."\n\
exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 eduTrack.wsgi:application' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
