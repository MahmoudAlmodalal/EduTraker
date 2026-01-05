"""
URL configuration for the manager app.

RESTful URL patterns for School, AcademicYear, Grade, Course, and ClassRoom management.
"""
from django.urls import path

from manager.views.school_views import (
    SchoolListApi,
    SchoolCreateApi,
    SchoolDetailApi,
    AcademicYearListApi,
    AcademicYearCreateApi,
    GradeListApi,
    GradeCreateApi,
    CourseListApi,
    CourseCreateApi,
    ClassRoomListApi,
    ClassRoomCreateApi,
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

    # Grade endpoints (global)
    path('grades/', GradeListApi.as_view(), name='grade-list'),
    path('grades/create/', GradeCreateApi.as_view(), name='grade-create'),

    # Course endpoints (nested under school)
    path('schools/<int:school_id>/courses/', CourseListApi.as_view(), name='course-list'),
    path('schools/<int:school_id>/courses/create/', CourseCreateApi.as_view(), name='course-create'),

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
]
