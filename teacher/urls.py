from django.urls import path

from teacher.views.assignment_views import (
    AssignmentListCreateApi,
    AssignmentDetailApi,
)

app_name = 'teacher'

urlpatterns = [
    # Assignment Management
    path('assignments/', AssignmentListCreateApi.as_view(), name='assignment-list-create'),
    path('assignments/<int:assignment_id>/', AssignmentDetailApi.as_view(), name='assignment-detail'),
]
