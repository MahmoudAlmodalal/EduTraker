"""
Script to create a superuser programmatically.
Run this with: python manage.py shell < create_superuser.py
Or use: python manage.py shell and paste the code.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduTrack.settings')
django.setup()

from accounts.models import CustomUser, Role

# Create superuser
email = input("Enter email: ")
full_name = input("Enter full name: ")
password = input("Enter password: ")

try:
    user = CustomUser.objects.create_superuser(
        email=email,
        full_name=full_name,
        password=password
    )
    print(f"Superuser created successfully: {user.email}")
except Exception as e:
    print(f"Error creating superuser: {e}")

