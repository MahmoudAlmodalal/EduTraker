from django.urls import path

from teacher.views.teacher_views import (
    TeacherListApi,
    TeacherCreateApi,
    TeacherDetailApi,
    TeacherDeactivateApi,
    TeacherActivateApi,
)
from teacher.views.assignment_views import (
    AssignmentListCreateApi,
    AssignmentDetailApi,
    AssignmentDeactivateApi,
    AssignmentActivateApi,
)
from teacher.views.attendance_views import (
    AttendanceListApi,
    AttendanceRecordApi,
    AttendanceDetailApi,
    AttendanceDeactivateApi,
    AttendanceActivateApi,
)
from teacher.views.mark_views import (
    MarkListApi,
    MarkRecordApi,
    MarkDetailApi,
    MarkDeactivateApi,
    MarkActivateApi,
    BulkMarkImportApi,
    KnowledgeGapListApi,
)
from teacher.views.learning_material_views import (
    LearningMaterialListCreateView,
    LearningMaterialDetailView,
)
from teacher.views.lesson_plan_views import (
    LessonPlanListCreateAPIView,
    LessonPlanRetrieveUpdateDestroyAPIView,
)

app_name = 'teacher'

urlpatterns = [
    # Teacher Management
    path('teachers/', TeacherListApi.as_view(), name='teacher-list'),
    path('teachers/create/', TeacherCreateApi.as_view(), name='teacher-create'),
    path('teachers/<int:teacher_id>/', TeacherDetailApi.as_view(), name='teacher-detail'),
    path('teachers/<int:teacher_id>/deactivate/', TeacherDeactivateApi.as_view(), name='teacher-deactivate'),
    path('teachers/<int:teacher_id>/activate/', TeacherActivateApi.as_view(), name='teacher-activate'),

    # Assignment Management
    path('assignments/', AssignmentListCreateApi.as_view(), name='assignment-list-create'),
    path('assignments/<int:assignment_id>/', AssignmentDetailApi.as_view(), name='assignment-detail'),
    path('assignments/<int:assignment_id>/deactivate/', AssignmentDeactivateApi.as_view(), name='assignment-deactivate'),
    path('assignments/<int:assignment_id>/activate/', AssignmentActivateApi.as_view(), name='assignment-activate'),

    # Attendance Management
    path('attendance/', AttendanceListApi.as_view(), name='attendance-list'),
    path('attendance/record/', AttendanceRecordApi.as_view(), name='attendance-record'),
    path('attendance/<int:attendance_id>/', AttendanceDetailApi.as_view(), name='attendance-detail'),
    path('attendance/<int:attendance_id>/deactivate/', AttendanceDeactivateApi.as_view(), name='attendance-deactivate'),
    path('attendance/<int:attendance_id>/activate/', AttendanceActivateApi.as_view(), name='attendance-activate'),

    # Mark Management
    path('marks/', MarkListApi.as_view(), name='mark-list'),
    path('marks/record/', MarkRecordApi.as_view(), name='mark-record'),
    path('marks/<int:mark_id>/', MarkDetailApi.as_view(), name='mark-detail'),
    path('marks/<int:mark_id>/deactivate/', MarkDeactivateApi.as_view(), name='mark-deactivate'),
    path('marks/<int:mark_id>/activate/', MarkActivateApi.as_view(), name='mark-activate'),

    # Learning Materials
    path('learning-materials/', LearningMaterialListCreateView.as_view(), name='learning-material-list-create'),
    path('learning-materials/<int:pk>/', LearningMaterialDetailView.as_view(), name='learning-material-detail'),

    # Lesson Plans
    path('lesson-plans/', LessonPlanListCreateAPIView.as_view(), name='lesson-plan-list-create'),
    path('lesson-plans/<int:pk>/', LessonPlanRetrieveUpdateDestroyAPIView.as_view(), name='lesson-plan-detail'),
    path('marks/bulk-import/', BulkMarkImportApi.as_view(), name='mark-bulk-import'),
    path('analytics/knowledge-gaps/', KnowledgeGapListApi.as_view(), name='knowledge-gaps'),
]
