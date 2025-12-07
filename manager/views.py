from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Q
from django.utils import timezone
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Workstream, StaffEvaluation, DepartmentActivityReport
from .serializers import (
    WorkstreamSerializer,
    StaffEvaluationSerializer,
    DepartmentActivityReportSerializer,
    CreateStaffAccountSerializer,
)

User = get_user_model()


class IsManager(permissions.BasePermission):
    """
    Simple role-based check. Assumes User has a 'role' field == 'manager'.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "manager"
        )

class IsAdminOrManager(permissions.BasePermission):
    """Permission check for Admin or Manager role."""
    def has_permission(self, request, view):
        user_role = getattr(request.user, "role", None)
        return bool(
            request.user
            and request.user.is_authenticated
            and user_role in ["admin", "manager"]
        )

class WorkstreamViewSet(viewsets.ModelViewSet):
    """
    Workstream management (Admin/Manager).
    """
    queryset = Workstream.objects.all()
    serializer_class = WorkstreamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Managers see only their workstream, admins see all."""
        qs = super().get_queryset()
        if getattr(self.request.user, "role", None) == "manager":
            return qs.filter(manager=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["get"])
    def statistics(self, request, pk=None):
        """Get statistics for a specific workstream."""
        workstream = self.get_object()
        
        # Calculate attendance statistics
        reports = DepartmentActivityReport.objects.filter(workstream=workstream)
        avg_attendance = reports.aggregate(Avg("attendance_rate"))["attendance_rate__avg"] or 0
        
        # Calculate evaluation statistics
        evaluations = StaffEvaluation.objects.filter(workstream=workstream)
        avg_score = evaluations.aggregate(Avg("score"))["score__avg"]
        
        data = {
            "workstream_id": workstream.id,
            "workstream_name": workstream.name,
            "total_reports": reports.count(),
            "avg_attendance_rate": round(float(avg_attendance), 2),
            "total_evaluations": evaluations.count(),
            "avg_evaluation_score": round(float(avg_score), 2) if avg_score else None,
        }
        
        return Response(data)

class StaffEvaluationViewSet(viewsets.ModelViewSet):
    """
    Staff evaluations (US-Manager-003).
    FR-RA-004: Managers can conduct staff evaluations.
    """
    queryset = StaffEvaluation.objects.all()
    serializer_class = StaffEvaluationSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)

    def get_queryset(self):
        """Managers see only their evaluations."""
        qs = super().get_queryset()
        if getattr(self.request.user, "role", None) == "manager":
            return qs.filter(manager=self.request.user)
        return qs.none()

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Get summary of all evaluations."""
        evaluations = self.get_queryset()
        
        data = {
            "total_evaluations": evaluations.count(),
            "avg_score": evaluations.aggregate(Avg("score"))["score__avg"],
            "by_teacher": evaluations.values("teacher__email", "teacher__first_name", "teacher__last_name")
                .annotate(avg_score=Avg("score"), count=Count("id")),
        }
        
        return Response(data)

class DepartmentActivityReportViewSet(viewsets.ModelViewSet):
    """
    Monitoring academic performance & department activity (US-Manager-001/002).
    """
    queryset = DepartmentActivityReport.objects.all()
    serializer_class = DepartmentActivityReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self.request.user, "role", None) == "manager":
            qs = qs.filter(manager=self.request.user)

            # Filter by date range
            date_from = self.request.query_params.get("date_from", None)
            date_to = self.request.query_params.get("date_to", None)
            if date_from:
                qs = qs.filter(date__gte=date_from)
            if date_to:
                qs = qs.filter(date__lte=date_to)
        
            return qs.order_by("-date") if qs else qs.none()
    
    @action(detail=False, methods=["get"])
    def daily_analysis(self, request):
        """
        Daily analysis showing student attendance rate for each class (US-Manager-001).
        """
        reports = self.get_queryset()
        
        # Get today's reports or most recent
        today = timezone.now().date()
        today_reports = reports.filter(date=today)
        
        if not today_reports.exists():
            # If no reports for today, get most recent
            today_reports = reports.order_by("-date")[:10]
        
        data = {
            "date": today,
            "total_reports": today_reports.count(),
            "reports": DepartmentActivityReportSerializer(today_reports, many=True).data,
            "avg_attendance_rate": today_reports.aggregate(Avg("attendance_rate"))["attendance_rate__avg"] or 0,
        }
        
        return Response(data)

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get aggregated statistics for all department reports."""
        reports = self.get_queryset()
        
        data = {
            "total_reports": reports.count(),
            "avg_attendance_rate": reports.aggregate(Avg("attendance_rate"))["attendance_rate__avg"] or 0,
            "by_workstream": reports.values("workstream__name", "workstream__id")
                .annotate(
                    count=Count("id"),
                    avg_attendance=Avg("attendance_rate")
                ),
        }
        
        return Response(data)


class CreateStaffAccountView(APIView):
    """
    Manager creates secretary / teacher accounts (US-Manager-004).

    POST:
    {
      "first_name": "...",
      "last_name": "...",
      "email": "...",
      "password": "...",
      "role": "teacher" | "secretary"
    }
    """
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def post(self, request, *args, **kwargs):
        serializer = CreateStaffAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(CreateStaffAccountSerializer(user).data, status=201)

class ManagerDashboardView(APIView):
    """
    Manager dashboard with overview statistics.
    """
    permission_classes = [permissions.IsAuthenticated, IsManager]
    
    def get(self, request):
        """Get dashboard data for the manager."""
        manager = request.user
        
        # Get manager's workstream
        try:
            workstream = manager.managed_workstream
        except Workstream.DoesNotExist:
            workstream = None
        
        # Get statistics
        reports = DepartmentActivityReport.objects.filter(manager=manager)
        evaluations = StaffEvaluation.objects.filter(manager=manager)
        
        data = {
            "manager": {
                "id": manager.id,
                "email": manager.email,
                "name": f"{manager.first_name} {manager.last_name}".strip() or manager.email,
            },
            "workstream": WorkstreamSerializer(workstream).data if workstream else None,
            "statistics": {
                "total_reports": reports.count(),
                "avg_attendance_rate": reports.aggregate(Avg("attendance_rate"))["attendance_rate__avg"] or 0,
                "total_evaluations": evaluations.count(),
                "avg_evaluation_score": evaluations.aggregate(Avg("score"))["score__avg"],
            },
            "recent_reports": DepartmentActivityReportSerializer(
                reports.order_by("-date")[:5], many=True
            ).data,
            "recent_evaluations": StaffEvaluationSerializer(
                evaluations.order_by("-created_at")[:5], many=True
            ).data,
        }
        
        return Response(data)