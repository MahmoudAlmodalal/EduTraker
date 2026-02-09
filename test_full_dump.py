
import sys
import json
import datetime
import decimal
from django.contrib.auth import get_user_model
from reports.services.count_services import get_comprehensive_statistics
from reports.services.activity_services import get_login_activity_chart

User = get_user_model()
user_id = 90001

def log(msg):
    # Write directly to stderr to maybe bypass buffering issues if stdout hangs
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()

class TracingEncoder(json.JSONEncoder):
    def default(self, obj):
        # log(f"Encoding object type: {type(obj)}")
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        try:
             # If it's a Django model, this might trigger
             if hasattr(obj, '_meta'):
                 log(f"ENCOUNTERED DJANGO MODEL: {type(obj)} - {obj}")
                 return str(obj)
        except:
            pass
        return super().default(obj)
    
    def encode(self, o):
        # We can recursively trace here to see where we are before crashing
        # But standard encode calls iterencode
        return super().encode(o)
    
    def iterencode(self, o, _one_shot=False):
        # This is where the magic happens usually
        return super().iterencode(o, _one_shot=_one_shot)

try:
    user = User.objects.get(id=user_id)
    log(f"Testing for user: {user.full_name}")
    
    data = get_comprehensive_statistics(actor=user)
    data['activity_chart'] = get_login_activity_chart()
    
    log("Starting JSON dump...")
    json_str = json.dumps(data, cls=TracingEncoder, indent=2)
    log("JSON dump finished successfully.")
    
except Exception as e:
    log(f"Error: {e}")
