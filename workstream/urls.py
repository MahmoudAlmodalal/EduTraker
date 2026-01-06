from django.urls import path
from workstream.views.workstream_views import (
    WorkstreamInfoView,
    WorkstreamListView,
    WorkstreamCreateView,
    WorkstreamDetailView,
    WorkstreamUpdateView,
    WorkstreamDeactivateView,
)

urlpatterns = [
    # Public endpoint for login page
    path('workstreams/<int:workstream_id>/info/', WorkstreamInfoView.as_view(), name='workstream-info'),
    
    # Workstream management endpoints
    path('workstreams/', WorkstreamListView.as_view(), name='workstream-list'),
    path('workstreams/create/', WorkstreamCreateView.as_view(), name='workstream-create'),
    path('workstreams/<int:workstream_id>/', WorkstreamDetailView.as_view(), name='workstream-detail'),
    path('workstreams/<int:workstream_id>/update/', WorkstreamUpdateView.as_view(), name='workstream-update'),
    path('workstreams/<int:workstream_id>/deactivate/', WorkstreamDeactivateView.as_view(), name='workstream-deactivate'),
]

