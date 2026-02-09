
import json
import datetime
import decimal
from django.contrib.auth import get_user_model
from reports.services.count_services import get_comprehensive_statistics
from reports.services.activity_services import get_login_activity_chart

User = get_user_model()
user_id = 90001 # Workstream Manager

def json_default(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    return f"<<Non-serializable: {type(obj)}: {obj}>>"

try:
    user = User.objects.get(id=user_id)
    print(f"Testing for user: {user.full_name} ({user.role})")
    
    # 1. Test get_comprehensive_statistics
    try:
        stats = get_comprehensive_statistics(actor=user)
        print("get_comprehensive_statistics: OK")
    except Exception as e:
        print(f"get_comprehensive_statistics FAILED: {e}")
        stats = {}

    # 2. Test get_login_activity_chart
    try:
        chart = get_login_activity_chart()
        print("get_login_activity_chart: OK")
        stats['activity_chart'] = chart
    except Exception as e:
        print(f"get_login_activity_chart FAILED: {e}")

    # 3. Test Serialization manually
    print("Attempting to dump JSON...")
    try:
        json_str = json.dumps(stats, default=json_default, indent=2)
        print("Serialization: OK")
        # print(json_str)
    except Exception as e:
        print(f"Serialization FAILED: {e}")
        
    # Check specifically for school.manager issues
    if 'statistics' in stats and 'summary' in stats['statistics']:
        summary = stats['statistics']['summary']
        print(f"Summary keys: {summary.keys()}")
        if 'by_school' in summary:
            print(f"Found {len(summary['by_school'])} schools in summary")
            for i, school in enumerate(summary['by_school']):
                 print(f"School {i}: {school.keys()}")

except Exception as e:
    print(f"Top Level Error: {e}")
