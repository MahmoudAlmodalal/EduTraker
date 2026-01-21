"""
URL configuration for the student app.

RESTful URL patterns for Student and StudentEnrollment management.
"""
from django.urls import path

from student.views.student_views import (
    StudentListApi,
    StudentCreateApi,
    StudentDetailApi,
    StudentDeactivateApi,
    StudentActivateApi,
)
from student.views.enrollment_views import (
    StudentEnrollmentListApi,
    EnrollmentCreateApi,
    EnrollmentDetailApi,
    EnrollmentDeactivateApi,
    EnrollmentActivateApi,
)

app_name = 'student'

urlpatterns = [
    # Student endpoints
    path('students/', StudentListApi.as_view(), name='student-list'),
    path('students/create/', StudentCreateApi.as_view(), name='student-create'),
    path('students/<int:student_id>/', StudentDetailApi.as_view(), name='student-detail'),
    path('students/<int:student_id>/deactivate/', StudentDeactivateApi.as_view(), name='student-deactivate'),
    path('students/<int:student_id>/activate/', StudentActivateApi.as_view(), name='student-activate'),

    # Student Enrollment endpoints (nested under student)
    path('students/<int:student_id>/enrollments/', StudentEnrollmentListApi.as_view(), name='student-enrollment-list'),

    # Enrollment endpoints (standalone)
    path('enrollments/create/', EnrollmentCreateApi.as_view(), name='enrollment-create'),
    path('enrollments/<int:enrollment_id>/', EnrollmentDetailApi.as_view(), name='enrollment-detail'),
    path('enrollments/<int:enrollment_id>/deactivate/', EnrollmentDeactivateApi.as_view(), name='enrollment-deactivate'),
    path('enrollments/<int:enrollment_id>/activate/', EnrollmentActivateApi.as_view(), name='enrollment-activate'),
]
