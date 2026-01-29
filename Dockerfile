FROM python:3.10-slim

# Prevent Python from writing .pyc files and buffer logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies for MySQL client and healthchecks
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy project files
COPY . .

# Create an entrypoint script to handle migrations and wait for DB
RUN echo '#!/bin/sh\n\
echo "Waiting for database..."\n\
while ! nc -z $DB_HOST 3306; do\n\
  sleep 0.1\n\
done\n\
echo "Database started"\n\
\n\
python manage.py migrate --noinput\n\
python manage.py collectstatic --noinput\n\
\n\
exec gunicorn --bind 0.0.0.0:8000 eduTrack.wsgi:application' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
