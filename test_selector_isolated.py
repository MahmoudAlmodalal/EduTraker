import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduTrack.settings')
django.setup()

from accounts.models import CustomUser, Role
from workstream.models import WorkStream
from workstream.selectors.workstream_selectors import workstream_list

def test_selector():
    # Cleanup
    WorkStream.all_objects.all().delete()
    CustomUser.all_objects.all().delete()

    admin = CustomUser.objects.create_superuser(
        email='admin_test@example.com',
        password='password123',
        full_name='Admin Test'
    )
    
    ws = WorkStream.objects.create(
        workstream_name="SearchableUnique",
        description="Test",
        capacity=10
    )
    
    print(f"Created WorkStream: {ws.id}, name={ws.workstream_name}, is_active={ws.is_active}")
    
    # Test list
    results = workstream_list(filters={}, user=admin)
    print(f"Results with no filter: {results.count()}")
    
    # Test search
    results_search = workstream_list(filters={'search': 'SearchableUnique'}, user=admin)
    print(f"Results with search: {results_search.count()}")
    for item in results_search:
        print(f" - {item.workstream_name}")

if __name__ == "__main__":
    test_selector()
