from django.urls import path
from workstream.views.workstream_view import (
    WorkstreamListView,
    WorkstreamCreateView,
    WorkstreamDetailView,
    WorkstreamUpdateView,
    WorkstreamDeactivateView,
)

urlpatterns = [
    # Workstream management endpoints
    path('workstreams/', WorkstreamListView.as_view(), name='workstream-list'),
    path('workstreams/create/', WorkstreamCreateView.as_view(), name='workstream-create'),
    path('workstreams/<int:workstream_id>/', WorkstreamDetailView.as_view(), name='workstream-detail'),
    path('workstreams/<int:workstream_id>/update/', WorkstreamUpdateView.as_view(), name='workstream-update'),
    path('workstreams/<int:workstream_id>/deactivate/', WorkstreamDeactivateView.as_view(), name='workstream-deactivate'),
]