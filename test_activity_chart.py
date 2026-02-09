
import sys
import json
from reports.services.activity_services import get_login_activity_chart
from rest_framework.renderers import JSONRenderer

renderer = JSONRenderer()

def log(msg):
    print(msg)
    sys.stdout.flush()

try:
    log("Calling get_login_activity_chart...")
    chart = get_login_activity_chart()
    log(f"Chart returned. Type: {type(chart)}")
    
    if isinstance(chart, list):
        log(f"Chart length: {len(chart)}")
        if len(chart) > 0:
            log(f"First item keys: {list(chart[0].keys())}")
            log(f"First item values: {chart[0]}")
            
    log("Serializing chart...")
    renderer.render(chart)
    log("Chart Serialization OK")

except Exception as e:
    log(f"Error: {e}")
