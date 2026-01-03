from django.urls import path
from workstream.views.workstream_views import WorkStreamCreateView

urlpatterns = [
    path("workstreams/", WorkStreamCreateView.as_view(), name="workstream-create"),
]

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
>>>>>>> c1334ecd7deabea52a3e42fd6d05fe1c8cf0a413
