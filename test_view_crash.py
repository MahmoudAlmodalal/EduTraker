
import sys
import os
from django.conf import settings
from rest_framework.test import APIRequestFactory, force_authenticate
from reports.views.stats_views import DashboardStatisticsView
from django.contrib.auth import get_user_model

User = get_user_model()
user_id = 90001

def log(msg):
    # print(msg)
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()

try:
    user = User.objects.get(id=user_id)
    log(f"Testing View for user: {user.full_name}")
    
    factory = APIRequestFactory()
    request = factory.get('/api/statistics/dashboard/')
    force_authenticate(request, user=user)
    
    log("Calling view...")
    view = DashboardStatisticsView.as_view()
    response = view(request)
    
    log(f"View returned. Status: {response.status_code}")
    log(f"Response Data keys: {response.data.keys() if hasattr(response, 'data') else 'No data'}")
    
    if hasattr(response, 'render'):
        log("Rendering response...")
        response.render()
        log("Render successful")
        log(f"Content length: {len(response.content)}")
    
except Exception as e:
    log(f"Error: {e}")
