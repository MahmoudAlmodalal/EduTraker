
import traceback
import json
from django.contrib.auth import get_user_model
from reports.services.count_services import get_comprehensive_statistics
from reports.services.activity_services import get_login_activity_chart
from rest_framework.renderers import JSONRenderer

User = get_user_model()
user_id = 90001

try:
    user = User.objects.get(id=user_id)
    print(f"Testing for user: {user.full_name}")
    
    stats = get_comprehensive_statistics(actor=user)
    stats['activity_chart'] = get_login_activity_chart()
    
    print("Data calculation successful. Attempting serialization...")
    
    # Try DRF JSON Renderer
    json_output = JSONRenderer().render(stats)
    print("Serialization successful!")
    print(f"Output size: {len(json_output)} bytes")
    # print(json_output.decode('utf-8')[:1000])

except Exception:
    traceback.print_exc()
