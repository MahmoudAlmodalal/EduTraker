from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from reports.models import UserLoginHistory
from typing import List, Dict

def get_login_activity_chart(days: int = 7) -> List[Dict]:
    """
    Get login frequency data for the last N days.
    
    Args:
        days: Number of days to look back (default 7)
    
    Returns:
        List of dictionaries with 'name' (day), 'logins', and 'date'
    """
    cutoff_date = timezone.now() - timedelta(days=days-1)
    
    login_stats = UserLoginHistory.objects.filter(
        login_time__gte=cutoff_date
    ).annotate(
        date=TruncDate('login_time')
    ).values('date').annotate(
        logins=Count('id')
    ).order_by('date')
    
    chart_data_map = {item['date']: item['logins'] for item in login_stats}
    
    activity_chart = []
    for i in range(days):
        day = cutoff_date.date() + timedelta(days=i)
        day_name = day.strftime("%a") # Mon, Tue, etc.
        count = chart_data_map.get(day, 0)
        activity_chart.append({
            'name': day_name,
            'logins': count,
            'date': str(day)
        })
        
    return activity_chart
