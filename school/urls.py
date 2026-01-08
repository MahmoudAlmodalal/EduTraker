# school/urls.py

from django.urls import path
from school.views.school_views import (
    SchoolListCreateAPIView,
    SchoolUpdateAPIView,
    SchoolDeactivateAPIView,
)

urlpatterns = [
    path("", SchoolListCreateAPIView.as_view(), name="school-list-create"),
    path("<int:school_id>/", SchoolUpdateAPIView.as_view(), name="school-update"),
    path("<int:school_id>/deactivate/", SchoolDeactivateAPIView.as_view(), name="school-deactivate"),
]
