from django.urls import path
from workstream.views.workstream_views import (
    WorkstreamInfoView,
    WorkstreamListCreateAPIView,
    WorkstreamUpdateAPIView,
    WorkstreamDeactivateAPIView,
)

app_name = 'workstream'

urlpatterns = [
    # Public endpoint for login page
    path('workstreams/<int:workstream_id>/info/', WorkstreamInfoView.as_view(), name='workstream-info'),
    # Workstream list and create endpoints
    path('workstream/', WorkstreamListCreateAPIView.as_view(), name='workstream-list-create'),
    
    # Workstream management endpoints
    path('workstreams/<int:workstream_id>/update/', WorkstreamUpdateAPIView.as_view(), name='workstream-update'),
    path('workstreams/<int:workstream_id>/deactivate/', WorkstreamDeactivateAPIView.as_view(), name='workstream-deactivate'),
]

