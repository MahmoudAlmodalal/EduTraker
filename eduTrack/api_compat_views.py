"""
Compatibility stub views for frontend API endpoints that don't have
dedicated backend implementations yet. These return safe empty/default
responses so the frontend doesn't encounter unexpected errors.

TODO: Replace each stub with a real implementation and add role-specific
permission classes (e.g., IsTeacher, IsSecretary) when building out
these features.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


class TeacherScheduleView(APIView):
    """Stub: return an empty schedule list for the given date."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"results": [], "count": 0}, status=status.HTTP_200_OK)


class SecretaryPendingTasksView(APIView):
    """Stub: return an empty list of pending tasks."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"results": [], "count": 0}, status=status.HTTP_200_OK)


class SecretaryUpcomingEventsView(APIView):
    """Stub: return an empty list of upcoming events."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"results": [], "count": 0}, status=status.HTTP_200_OK)


class SchoolPerformanceView(APIView):
    """Stub: return empty school performance data."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "performance": [],
            "period": request.query_params.get("period", "monthly"),
        }, status=status.HTTP_200_OK)


class NotificationAlertsView(APIView):
    """Stub: return an empty alerts list."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"results": [], "count": 0}, status=status.HTTP_200_OK)
