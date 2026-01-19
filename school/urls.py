# school/urls.py

from django.urls import path
from school.views.school_views import (
    SchoolCreateAPIView,
    SchoolListAPIView,
    SchoolUpdateAPIView,
    SchoolDeactivateAPIView,
    SchoolActivateAPIView,
)
from school.views.academic_year_views import (
    AcademicYearListAPIView,
    AcademicYearCreateAPIView,
    AcademicYearDetailAPIView,
    AcademicYearUpdateAPIView,
    AcademicYearDeactivateAPIView,
    AcademicYearActivateAPIView,
)
from school.views.grade_views import (
    GradeListApi,
    GradeCreateApi,
    GradeDetailApi,
    GradeDeactivateApi,
    GradeActivateApi,
)
from school.views.course_views import (
    CourseListApi,
    CourseCreateApi,
    CourseDetailApi,
    CourseDeactivateApi,
    CourseActivateApi,
)
from school.views.class_room_views import (
    ClassRoomListApi,
    ClassRoomCreateApi,
    ClassRoomDetailApi,
    ClassRoomDeactivateApi,
    ClassRoomActivateApi,
)

urlpatterns = [
    # School endpoints
    path("school/", SchoolListAPIView.as_view(), name="school-list"),
    path("school/create/", SchoolCreateAPIView.as_view(), name="school-create"),
    path("school/<int:school_id>/update/", SchoolUpdateAPIView.as_view(), name="school-update"),
    path("school/<int:school_id>/deactivate/", SchoolDeactivateAPIView.as_view(), name="school-deactivate"),
    path("school/<int:school_id>/activate/", SchoolActivateAPIView.as_view(), name="school-activate"),
    
    # Academic Year endpoints
    path("academic-years/", AcademicYearListAPIView.as_view(), name="academic-year-list"),
    path("academic-years/create/", AcademicYearCreateAPIView.as_view(), name="academic-year-create"),
    path("academic-years/<int:academic_year_id>/", AcademicYearDetailAPIView.as_view(), name="academic-year-detail"),
    path("academic-years/<int:academic_year_id>/update/", AcademicYearUpdateAPIView.as_view(), name="academic-year-update"),
    path("academic-years/<int:academic_year_id>/deactivate/", AcademicYearDeactivateAPIView.as_view(), name="academic-year-deactivate"),
    path("academic-years/<int:academic_year_id>/activate/", AcademicYearActivateAPIView.as_view(), name="academic-year-activate"),

    # Grade endpoints
    path("grades/", GradeListApi.as_view(), name="grade-list"),
    path("grades/create/", GradeCreateApi.as_view(), name="grade-create"),
    path("grades/<int:grade_id>/", GradeDetailApi.as_view(), name="grade-detail"),
    path("grades/<int:grade_id>/deactivate/", GradeDeactivateApi.as_view(), name="grade-deactivate"),
    path("grades/<int:grade_id>/activate/", GradeActivateApi.as_view(), name="grade-activate"),

    # Course endpoints
    path("school/<int:school_id>/courses/", CourseListApi.as_view(), name="course-list"),
    path("school/<int:school_id>/courses/create/", CourseCreateApi.as_view(), name="course-create"),
    path("school/<int:school_id>/courses/<int:course_id>/", CourseDetailApi.as_view(), name="course-detail"),
    path("school/<int:school_id>/courses/<int:course_id>/deactivate/", CourseDeactivateApi.as_view(), name="course-deactivate"),
    path("school/<int:school_id>/courses/<int:course_id>/activate/", CourseActivateApi.as_view(), name="course-activate"),

    # Classroom endpoints
    path("school/<int:school_id>/academic-year/<int:academic_year_id>/classrooms/", ClassRoomListApi.as_view(), name="classroom-list"),
    path("school/<int:school_id>/academic-year/<int:academic_year_id>/classrooms/create/", ClassRoomCreateApi.as_view(), name="classroom-create"),
    path("school/<int:school_id>/academic-year/<int:academic_year_id>/classrooms/<int:classroom_id>/", ClassRoomDetailApi.as_view(), name="classroom-detail"),
    path("school/<int:school_id>/academic-year/<int:academic_year_id>/classrooms/<int:classroom_id>/deactivate/", ClassRoomDeactivateApi.as_view(), name="classroom-deactivate"),
    path("school/<int:school_id>/academic-year/<int:academic_year_id>/classrooms/<int:classroom_id>/activate/", ClassRoomActivateApi.as_view(), name="classroom-activate"),
]
