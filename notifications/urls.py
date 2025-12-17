from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    WorkstreamViewSet,
    StaffEvaluationViewSet,
    DepartmentActivityReportViewSet,
    CreateStaffAccountView,
    ManagerDashboardView,
)

router = DefaultRouter()
router.register(r"workstreams", WorkstreamViewSet, basename="workstream")
router.register(r"staff-evaluations", StaffEvaluationViewSet, basename="staff-evaluation")
router.register(
    r"department-reports",
    DepartmentActivityReportViewSet,
    basename="department-report",
)

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/staff-accounts/", CreateStaffAccountView.as_view(), name="create-staff-account"),
     path("api/dashboard/", ManagerDashboardView.as_view(), name="manager-dashboard"),
]