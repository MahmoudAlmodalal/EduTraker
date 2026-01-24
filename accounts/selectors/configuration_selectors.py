from typing import Optional, Any
from django.db.models import Q
from accounts.models import SystemConfiguration
from workstream.models import WorkStream
from school.models import School

def config_get_value(
    config_key: str, 
    *, 
    school: Optional[School] = None, 
    work_stream: Optional[WorkStream] = None
) -> Optional[str]:
    """
    Retrieve configuration value with cascading priority:
    1. School-specific setting
    2. Workstream-specific setting (if school belongs to a workstream)
    3. Global setting (where school and workstream are null)
    
    Returns the config_value of the highest priority match, or None if not found.
    """
    # 1. Check School Specific
    if school:
        school_config = SystemConfiguration.objects.filter(
            school=school, 
            config_key=config_key,
            is_active=True
        ).first()
        if school_config:
            return school_config.config_value
        
        # If no school config, fallback to school's workstream if not provided
        if not work_stream:
            work_stream = school.work_stream

    # 2. Check Workstream Specific
    if work_stream:
        ws_config = SystemConfiguration.objects.filter(
            work_stream=work_stream, 
            config_key=config_key,
            school__isnull=True,
            is_active=True
        ).first()
        if ws_config:
            return ws_config.config_value

    # 3. Check Global Specific
    global_config = SystemConfiguration.objects.filter(
        school__isnull=True, 
        work_stream__isnull=True, 
        config_key=config_key,
        is_active=True
    ).first()
    
    if global_config:
        return global_config.config_value

    return None
