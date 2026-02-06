"""
URL configuration for eduTrack project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from teacher.views.attendance_views import AttendanceListApi
from teacher.views.mark_views import MarkListApi
from student.views.student_views import StudentListApi
from school.views.academic_year_views import AcademicYearListAPIView
from reports.views.stats_views import DashboardStatisticsView
from eduTrack.api_compat_views import (
    TeacherScheduleView,
    SecretaryPendingTasksView,
    SecretaryUpcomingEventsView,
    SchoolPerformanceView,
    NotificationAlertsView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ============================================
    # API DOCUMENTATION (Swagger/OpenAPI)
    # ============================================
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # ============================================
    # AUTHENTICATION ENDPOINTS
    # ============================================
    
    # All auth endpoints are defined in accounts.urls with full prefixes:
    # /api/portal/auth/...
    # /api/workstream/<id>/auth/...
    path('api/', include('accounts.urls')),
    path('api/', include('workstream.urls')),
    path('api/', include('reports.urls')),
    path('api/', include('school.urls')),
    path('api/manager/', include('manager.urls')),
    path('api/manager/', include('student.urls')),
    path('api/custom-admin/', include('custom_admin.urls')),
    path('api/workstream-manager/', include('workstream_manager.urls')),
    path('api/teacher/', include('teacher.urls')),
    path('api/guardian/', include('guardian.urls')),
    path('api/user-messages/', include('user_messages.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/secretary/', include('secretary.urls')),

    # ============================================
    # FRONTEND COMPATIBILITY ROUTES
    # ============================================
    # These aliases map frontend-expected URL paths to existing backend views
    # so the EduTrakerFront app can reach all endpoints cleanly.

    # Student-facing endpoints (frontend uses /student/ prefix).
    # The underlying views already enforce role-based filtering on the queryset,
    # so students only see their own attendance/marks.
    path('api/student/attendance/', AttendanceListApi.as_view(), name='compat-student-attendance'),
    path('api/student/marks/', MarkListApi.as_view(), name='compat-student-marks'),
    path('api/student/students/', StudentListApi.as_view(), name='compat-student-students'),

    # School academic years (frontend expects /school/academic-years/)
    path('api/school/academic-years/', AcademicYearListAPIView.as_view(), name='compat-school-academic-years'),

    # Reports prefix (frontend guardianService uses /reports/statistics/...)
    path('api/reports/statistics/dashboard/', DashboardStatisticsView.as_view(), name='compat-reports-dashboard'),
    path('api/reports/school-performance/', SchoolPerformanceView.as_view(), name='compat-school-performance'),

    # Stub endpoints for features not yet implemented
    path('api/teacher/schedule/', TeacherScheduleView.as_view(), name='compat-teacher-schedule'),
    path('api/secretary/tasks/pending/', SecretaryPendingTasksView.as_view(), name='compat-secretary-tasks'),
    path('api/secretary/events/upcoming/', SecretaryUpcomingEventsView.as_view(), name='compat-secretary-events'),
    path('api/notifications/alerts/', NotificationAlertsView.as_view(), name='compat-notification-alerts'),
]

