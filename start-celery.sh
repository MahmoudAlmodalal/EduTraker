#!/bin/bash
# Start Celery worker for background task processing

echo "Starting Celery worker..."
echo "Worker will run in this terminal and process background tasks."
echo ""

# Load environment variables from .env file
export $(grep -v '^#' /home/mahmoud/Desktop/front/.env | xargs)

cd /home/mahmoud/Desktop/front/EduTraker
celery -A eduTrack worker --loglevel=info
