"""
URL configuration for the manager app.

RESTful URL patterns for School, AcademicYear, Grade, Course, and ClassRoom management.
"""
from django.urls import path

from manager.views.school_views import (
    SchoolListApi,
    SchoolCreateApi,
    SchoolDetailApi,
)
from manager.views.academic_year_views import (
    AcademicYearListApi,
    AcademicYearCreateApi,
    AcademicYearDetailApi,
)
from manager.views.grade_views import (
    GradeListApi,
    GradeCreateApi,
    GradeDetailApi,
)
from manager.views.course_views import (
    CourseListApi,
    CourseCreateApi,
    CourseDetailApi,
)
from manager.views.class_room_views import (
    ClassRoomListApi,
    ClassRoomCreateApi,
    ClassRoomDetailApi,
)

from manager.views.staff_evaluation_views import (
    StaffEvaluationListApi,
    StaffEvaluationCreateApi,
    StaffEvaluationDetailApi,
)

app_name = 'manager'

urlpatterns = [
    # School endpoints
    path('schools/', SchoolListApi.as_view(), name='school-list'),
    path('schools/create/', SchoolCreateApi.as_view(), name='school-create'),
    path('schools/<int:school_id>/', SchoolDetailApi.as_view(), name='school-detail'),

    # Academic Year endpoints (nested under school)
    path('schools/<int:school_id>/academic-years/', AcademicYearListApi.as_view(), name='academic-year-list'),
    path('schools/<int:school_id>/academic-years/create/', AcademicYearCreateApi.as_view(), name='academic-year-create'),
    path('schools/<int:school_id>/academic-years/<int:academic_year_id>/', AcademicYearDetailApi.as_view(), name='academic-year-detail'),

    # Grade endpoints (global)
    path('grades/', GradeListApi.as_view(), name='grade-list'),
    path('grades/create/', GradeCreateApi.as_view(), name='grade-create'),
    path('grades/<int:grade_id>/', GradeDetailApi.as_view(), name='grade-detail'),

    # Course endpoints (nested under school)
    path('schools/<int:school_id>/courses/', CourseListApi.as_view(), name='course-list'),
    path('schools/<int:school_id>/courses/create/', CourseCreateApi.as_view(), name='course-create'),
    path('schools/<int:school_id>/courses/<int:course_id>/', CourseDetailApi.as_view(), name='course-detail'),

    # ClassRoom endpoints (nested under school and academic year)
    path(
        'schools/<int:school_id>/academic-years/<int:academic_year_id>/classrooms/',
        ClassRoomListApi.as_view(),
        name='classroom-list'
    ),
    path(
        'schools/<int:school_id>/academic-years/<int:academic_year_id>/classrooms/create/',
        ClassRoomCreateApi.as_view(),
        name='classroom-create'
    ),
    path(
        'schools/<int:school_id>/academic-years/<int:academic_year_id>/classrooms/<int:classroom_id>/',
        ClassRoomDetailApi.as_view(),
        name='classroom-detail'
    ),



    # Staff Evaluation endpoints
    path('staff-evaluations/', StaffEvaluationListApi.as_view(), name='staff-evaluation-list'),
    path('staff-evaluations/create/', StaffEvaluationCreateApi.as_view(), name='staff-evaluation-create'),
    path('staff-evaluations/<int:evaluation_id>/', StaffEvaluationDetailApi.as_view(), name='staff-evaluation-detail'),
]
