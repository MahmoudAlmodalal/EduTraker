from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime

from reports.models import ActivityLog
from reports.serializers import ActivityLogSerializer


class ActivityLogListView(APIView):
    """
    API endpoint to list activity logs with filtering and pagination.
    Only accessible to admin users.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Check if user is admin
        if request.user.role != 'admin':
            return Response(
                {"detail": "Only administrators can access activity logs."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get query parameters for filtering
        action_type = request.GET.get('action_type', None)
        actor_id = request.GET.get('actor_id', None)
        entity_type = request.GET.get('entity_type', None)
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        search = request.GET.get('search', None)
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 50))

        # Start with all activity logs
        queryset = ActivityLog.objects.select_related('actor').all()

        # Apply filters
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        
        if actor_id:
            queryset = queryset.filter(actor_id=actor_id)
        
        if entity_type:
            queryset = queryset.filter(entity_type__icontains=entity_type)
        
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
                Q(actor__full_name__icontains=search) |
                Q(actor__email__icontains=search)
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
