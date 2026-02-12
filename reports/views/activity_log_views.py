from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime

from reports.models import ActivityLog
from reports.serializers import ActivityLogSerializer
from accounts.models import Role
from school.models import School


class ActivityLogListView(APIView):
    """
    API endpoint to list activity logs with filtering and pagination.
    Accessible by admin and manager roles, with role-based scoping.
    """
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _normalize_user_type(value):
        if not value:
            return None

        raw = str(value).strip().lower()
        mapping = {
            "manager": Role.MANAGER_SCHOOL,
            "school_manager": Role.MANAGER_SCHOOL,
            "manager_school": Role.MANAGER_SCHOOL,
            "teacher": Role.TEACHER,
            "secretary": Role.SECRETARY,
            "admin": Role.ADMIN,
            "manager_workstream": Role.MANAGER_WORKSTREAM,
            "guest": Role.GUEST,
            "guardian": Role.GUARDIAN,
            "student": Role.STUDENT,
            "system": "system",
        }
        return mapping.get(raw, raw)

    @staticmethod
    def _apply_action_type_filter(queryset, action_type):
        if not action_type:
            return queryset

        raw = str(action_type).strip().upper()
        if raw in {"ALL", "ANY"}:
            return queryset
        if raw == "DEACTIVATE":
            return queryset.filter(action_type__iexact="UPDATE", description__icontains="deactivat")
        if raw == "ACTIVATE":
            return queryset.filter(
                action_type__iexact="UPDATE",
                description__icontains="activat"
            ).exclude(description__icontains="deactivat")

        return queryset.filter(action_type__iexact=raw)

    def get(self, request):
        user = request.user
        if user.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL, Role.SECRETARY]:
            return Response(
                {"detail": "You do not have permission to access activity logs."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get query parameters for filtering
        action_type = request.GET.get('action_type', None)
        user_type = request.GET.get('user_type', None)
        actor_id = request.GET.get('actor_id', None)
        entity_type = request.GET.get('entity_type', None)
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        school_id = request.GET.get('school_id', None)
        search = request.GET.get('search', None)
        try:
            page = max(int(request.GET.get('page', 1)), 1)
        except (TypeError, ValueError):
            page = 1
        try:
            page_size = int(request.GET.get('page_size', 20))
        except (TypeError, ValueError):
            page_size = 20
        page_size = min(max(page_size, 1), 100)

        # Start with all activity logs
        queryset = ActivityLog.objects.select_related('actor').all()

        # Apply role-based scope
        if user.role == Role.MANAGER_WORKSTREAM:
            allowed_school_ids = list(
                School.objects.filter(work_stream_id=user.work_stream_id).values_list('id', flat=True)
            )
            if school_id:
                try:
                    requested_school_id = int(school_id)
                except (TypeError, ValueError):
                    requested_school_id = None
                allowed_school_ids = (
                    [requested_school_id]
                    if requested_school_id in allowed_school_ids
                    else []
                )

            allowed_school_ids_str = [str(sid) for sid in allowed_school_ids]
            queryset = queryset.filter(
                Q(actor__school_id__in=allowed_school_ids) |
                Q(entity_type__iexact="School", entity_id__in=allowed_school_ids_str)
            )
        elif user.role in [Role.MANAGER_SCHOOL, Role.SECRETARY]:
            if not user.school_id:
                queryset = queryset.none()
            else:
                requested_school_id = user.school_id
                if school_id:
                    try:
                        requested_school_id = int(school_id)
                    except (TypeError, ValueError):
                        requested_school_id = user.school_id
                if requested_school_id != user.school_id:
                    queryset = queryset.none()
                else:
                    queryset = queryset.filter(
                        Q(actor__school_id=user.school_id) |
                        Q(entity_type__iexact="School", entity_id=str(user.school_id))
                    )
        else:
            # Admin can optionally scope by school
            if school_id:
                try:
                    requested_school_id = int(school_id)
                    queryset = queryset.filter(
                        Q(actor__school_id=requested_school_id) |
                        Q(entity_type__iexact="School", entity_id=str(requested_school_id))
                    )
                except (TypeError, ValueError):
                    pass

        # Apply filters
        queryset = self._apply_action_type_filter(queryset, action_type)
        
        if actor_id:
            queryset = queryset.filter(actor_id=actor_id)
        
        if entity_type:
            queryset = queryset.filter(entity_type__icontains=entity_type)

        normalized_user_type = self._normalize_user_type(user_type)
        if normalized_user_type == "system":
            queryset = queryset.filter(actor__isnull=True)
        elif normalized_user_type:
            queryset = queryset.filter(actor__role=normalized_user_type)
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                queryset = queryset.filter(created_at__gte=start_dt)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                queryset = queryset.filter(created_at__lte=end_dt)
            except ValueError:
                pass
        
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) |
                Q(entity_type__icontains=search) |
                Q(action_type__icontains=search) |
                Q(entity_id__icontains=search) |
                Q(actor__full_name__icontains=search) |
                Q(actor__email__icontains=search) |
                Q(actor__role__icontains=search)
            )

        # Order by most recent first
        queryset = queryset.order_by('-created_at')

        # Paginate results
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        # Serialize data
        serializer = ActivityLogSerializer(page_obj.object_list, many=True)

        return Response({
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'page_size': page_size,
            'next': page_obj.has_next(),
            'previous': page_obj.has_previous(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)
