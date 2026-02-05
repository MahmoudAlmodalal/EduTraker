#!/bin/bash
# Start all services for EduTraker with Celery background task processing

echo "Starting Redis..."
sudo systemctl start redis
redis-cli ping > /dev/null && echo "✓ Redis is running" || echo "✗ Redis failed to start"

echo ""
echo "Starting Django backend on port 8000..."
echo "Backend will run in this terminal. Open a new terminal to start Celery worker."
echo ""

# Load environment variables from .env file
export $(grep -v '^#' /home/mahmoud/Desktop/front/.env | xargs)

cd /home/mahmoud/Desktop/front/EduTraker
python manage.py runserver
