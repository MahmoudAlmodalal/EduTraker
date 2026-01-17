# school/urls.py

from django.urls import path
from school.views.school_views import (
    SchoolCreateAPIView,
    SchoolListAPIView,
    SchoolUpdateAPIView,
    SchoolDeactivateAPIView,
)
from school.views.academic_year_views import (
    AcademicYearListAPIView,
    AcademicYearCreateAPIView,
    AcademicYearDetailAPIView,
    AcademicYearUpdateAPIView,
    AcademicYearDeactivateAPIView,
)

urlpatterns = [
    # School endpoints
    path("school/", SchoolListAPIView.as_view(), name="school-list"),
    path("school/create/", SchoolCreateAPIView.as_view(), name="school-create"),
    path("school/<int:school_id>/update/", SchoolUpdateAPIView.as_view(), name="school-update"),
    path("school/<int:school_id>/deactivate/", SchoolDeactivateAPIView.as_view(), name="school-deactivate"),
    
    # Academic Year endpoints
    path("academic-years/", AcademicYearListAPIView.as_view(), name="academic-year-list"),
    path("academic-years/create/", AcademicYearCreateAPIView.as_view(), name="academic-year-create"),
    path("academic-years/<int:academic_year_id>/", AcademicYearDetailAPIView.as_view(), name="academic-year-detail"),
    path("academic-years/<int:academic_year_id>/update/", AcademicYearUpdateAPIView.as_view(), name="academic-year-update"),
    path("academic-years/<int:academic_year_id>/deactivate/", AcademicYearDeactivateAPIView.as_view(), name="academic-year-deactivate"),
]
