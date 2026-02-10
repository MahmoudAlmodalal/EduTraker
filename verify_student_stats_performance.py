import os
import django
import time
import json
from django.test import RequestFactory
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EduTraker.settings')
django.setup()

from reports.views.stats_views import DashboardStatisticsView
from accounts.models import CustomUser

def verify_performance():
    # Find a student user
    student_user = CustomUser.objects.filter(role='student').first()
    if not student_user:
        print("No student user found for testing.")
        return

    print(f"Testing performance for student: {student_user.email}")

    factory = RequestFactory()
    view = DashboardStatisticsView.as_view()

    # Create request
    request = factory.get('/api/reports/statistics/dashboard/')
    request.user = student_user

    # Measure time
    start_time = time.time()
    response = view(request)
    end_time = time.time()

    duration = end_time - start_time
    print(f"Dashboard Statistics View Response Time: {duration:.4f} seconds")

    if response.status_code == 200:
        data = response.data
        print("Response Data Structure Check:")
        print(f"Role: {data.get('role')}")
        print(f"Recent Activity Count: {len(data.get('recent_activity', []))}")
        print(f"Activity Chart Count: {len(data.get('activity_chart', []))}")
        
        stats = data.get('statistics', {})
        print(f"Statistics Categories: {list(stats.keys())}")
        
        # Ensure critical data is still there
        if 'profile' in stats and 'grades' in stats and 'attendance' in stats:
            print("SUCCESS: Critical statistics are present.")
        else:
            print("FAILURE: Missing critical statistics.")
    else:
        print(f"FAILURE: Status code {response.status_code}")
        print(response.data)

if __name__ == "__main__":
    verify_performance()
