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
# Fixed: Added check for DB_HOST and DB_PORT to avoid nc usage error if they are empty
RUN echo '#!/bin/sh\n\
if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then\n\
  echo "Waiting for database at $DB_HOST:$DB_PORT..."\n\
  while ! nc -z "$DB_HOST" "$DB_PORT"; do\n\
    sleep 1\n\
  done\n\
  echo "Database started"\n\
else\n\
  echo "DB_HOST or DB_PORT not set, skipping wait..."\n\
fi\n\
\n\
python manage.py migrate --noinput\n\
python manage.py collectstatic --noinput\n\
\n\
exec gunicorn --bind 0.0.0.0:8000 eduTrack.wsgi:application' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
