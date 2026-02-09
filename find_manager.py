
from accounts.models import CustomUser, Role

managers = CustomUser.objects.filter(role=Role.MANAGER_WORKSTREAM, is_active=True)[:5]
print(f"Found {managers.count()} active workstream managers:")
for manager in managers:
    print(f"ID: {manager.id}, Name: {manager.full_name}, Email: {manager.email}, Workstream ID: {manager.work_stream_id}")
