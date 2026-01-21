from django.urls import path

from guardian.views import (
    GuardianListCreateView,
    GuardianRetrieveUpdateView,
    GuardianDeactivateView,
    GuardianReactivateView,
    GuardianStudentLinkListCreateView,
    GuardianStudentLinkUpdateDeleteView,
)

urlpatterns = [
    path("guardians/", GuardianListCreateView.as_view(), name="guardian-list-create"),
    path("guardians/<int:guardian_user_id>/", GuardianRetrieveUpdateView.as_view(), name="guardian-retrieve-update"),
    path("guardians/<int:guardian_user_id>/deactivate/", GuardianDeactivateView.as_view(), name="guardian-deactivate"),
    path("guardians/<int:guardian_user_id>/reactivate/", GuardianReactivateView.as_view(), name="guardian-reactivate"),

    path(
        "guardians/<int:guardian_user_id>/students/",
        GuardianStudentLinkListCreateView.as_view(),
        name="guardian-student-link-list-create",
    ),
    path(
        "guardians/<int:guardian_user_id>/students/<int:student_id>/",
        GuardianStudentLinkUpdateDeleteView.as_view(),
        name="guardian-student-link-update-delete",
    ),
]

