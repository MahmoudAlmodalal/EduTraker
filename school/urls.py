# school/urls.py

from django.urls import path
from school.views.school_views import (
    SchoolListCreateAPIView,
    SchoolUpdateAPIView,
    SchoolDeactivateAPIView,
)
from school.views.academic_year_views import (
    AcademicYearCreateAPIView,
    AcademicYearUpdateAPIView,
    AcademicYearDeactivateAPIView,
)
urlpatterns = [
    path("", SchoolListCreateAPIView.as_view(), name="school-list-create"),
    path("<int:school_id>/", SchoolUpdateAPIView.as_view(), name="school-update"),
    path("<int:school_id>/deactivate/", SchoolDeactivateAPIView.as_view(), name="school-deactivate"),
    path("academic-years/", AcademicYearCreateAPIView.as_view(), name="academic-year-create"),
    path("academic-years/<int:academic_year_id>/", AcademicYearUpdateAPIView.as_view(), name="academic-year-update"),
    path("academic-years/<int:academic_year_id>/deactivate/", AcademicYearDeactivateAPIView.as_view(), name="academic-year-deactivate"),
]
