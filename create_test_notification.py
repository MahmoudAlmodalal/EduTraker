import os
import django
import sys

# Setup Django environment
sys.path.append('/home/mahmoud/Desktop/front/EduTraker')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduTrack.settings')
django.setup()

from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()

# Get the first user (likely the one logged in)
# Or try to find 'admin' or similar
user = User.objects.first()

if user:
    print(f"Creating notification for user: {user.email}")
    Notification.objects.create(
        recipient=user,
        title="VERIFICATION TEST",
        message="This is a real notification from the backend to verify the connection.",
        notification_type="system",
        is_read=False
    )
    print("Notification created successfully.")
else:
    print("No users found to attach notification to.")
