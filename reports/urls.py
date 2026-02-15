from django.urls import path
from reports.views.stats_views import (
    TeacherStudentCountView,
    WorkstreamStudentCountView,
    SchoolStudentCountView,
    SchoolManagerStudentCountView,
    CourseStudentCountView,
    ClassroomStudentCountView,
    ComprehensiveStatisticsView,
    DashboardStatisticsView,
    SchoolPerformanceView,
    EnrollmentTrendsView
)
from reports.views.export_views import ReportExportView
from reports.views.activity_log_views import ActivityLogListView

urlpatterns = [
    # Dashboard statistics (role-based)
    path('statistics/dashboard/', DashboardStatisticsView.as_view(), name='dashboard-statistics'),
    
    # Comprehensive statistics
    path('statistics/comprehensive/', ComprehensiveStatisticsView.as_view(), name='comprehensive-statistics'),
    path('statistics/enrollment-trends/', EnrollmentTrendsView.as_view(), name='enrollment-trends'),
    
    # Teacher statistics
    path('statistics/teacher/<int:teacher_id>/', TeacherStudentCountView.as_view(), name='teacher-student-count'),
    
    # Workstream statistics
    path('statistics/workstream/<int:workstream_id>/', WorkstreamStudentCountView.as_view(), name='workstream-student-count'),
    
    # School statistics
    path('statistics/school/<int:school_id>/', SchoolStudentCountView.as_view(), name='school-student-count'),
    
    # School Manager statistics
    path('statistics/school-manager/<int:manager_id>/', SchoolManagerStudentCountView.as_view(), name='school-manager-student-count'),
    
    # Course statistics
    path('statistics/course/<int:course_id>/', CourseStudentCountView.as_view(), name='course-student-count'),
    
    # Classroom statistics
    path('statistics/classroom/<int:classroom_id>/', ClassroomStudentCountView.as_view(), name='classroom-student-count'),
    
    # Export
    path('export/', ReportExportView.as_view(), name='report-export'),
    
    # Activity Logs
    path('activity-logs/', ActivityLogListView.as_view(), name='activity-logs'),
    
    # Performance
    path('school-performance/', SchoolPerformanceView.as_view(), name='school-performance'),
    path('school/<int:school_id>/performance/', SchoolPerformanceView.as_view(), name='school-performance-detail'),
]
