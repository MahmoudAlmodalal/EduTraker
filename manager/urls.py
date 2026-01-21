"""
URL configuration for the manager app.

RESTful URL patterns for School, AcademicYear, Grade, Course, and ClassRoom management.
"""
from django.urls import path

from manager.views.staff_evaluation_views import (
    StaffEvaluationListApi,
    StaffEvaluationCreateApi,
    StaffEvaluationDetailApi,
)

app_name = 'manager'

urlpatterns = [

    # Staff Evaluation endpoints
    path('staff-evaluations/', StaffEvaluationListApi.as_view(), name='staff-evaluation-list'),
    path('staff-evaluations/create/', StaffEvaluationCreateApi.as_view(), name='staff-evaluation-create'),
    path('staff-evaluations/<int:evaluation_id>/', StaffEvaluationDetailApi.as_view(), name='staff-evaluation-detail'),
]
