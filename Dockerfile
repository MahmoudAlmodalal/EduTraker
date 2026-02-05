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

# Ensure entrypoint is executable
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
