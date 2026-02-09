
import sys
import json
from django.contrib.auth import get_user_model
from reports.models import ActivityLog
from reports.serializers import ActivityLogSerializer
from school.models import School
from django.db.models import Q
from rest_framework.renderers import JSONRenderer

renderer = JSONRenderer()
User = get_user_model()
user_id = 90001

def log(msg):
    print(msg)
    sys.stdout.flush()

try:
    user = User.objects.get(id=user_id)
    log(f"Testing for user: {user.full_name}")
    
    # Replicate query logic from view
    workstream_id = getattr(user, 'work_stream_id', None)
    log(f"Workstream ID: {workstream_id}")
    
    query = Q(actor=user)
    if workstream_id:
        query |= Q(entity_type='Workstream', entity_id=str(workstream_id))
        school_ids = list(School.objects.filter(work_stream_id=workstream_id).values_list('id', flat=True))
        log(f"Found {len(school_ids)} schools")
        if school_ids:
            query |= Q(entity_type='School', entity_id__in=[str(sid) for sid in school_ids])
            
    log(f"Query constructed. Fetching logs...")
    recent_activity_qs = ActivityLog.objects.filter(query).order_by('-created_at')[:10]
    log(f"Queryset created. Count (with len):")
    # Force evaluation
    logs = list(recent_activity_qs)
    log(f"Logs count: {len(logs)}")
    
    if len(logs) > 0:
        log(f"First log: {logs[0]}")
        
    log("Serializing recent activity...")
    serializer = ActivityLogSerializer(logs, many=True)
    data = serializer.data
    log("Serializer.data accessed (list of dicts).")
    
    renderer.render(data)
    log("Serialization OK")

except Exception as e:
    log(f"Error: {e}")
