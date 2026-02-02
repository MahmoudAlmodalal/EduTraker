from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count

from custom_admin.models import SupportTicket
from custom_admin.serializers import SupportTicketSerializer, SupportTicketStatsSerializer


class SupportTicketListCreateView(ListCreateAPIView):
    """
    List all support tickets or create a new ticket.
    Supports filtering by status, priority, and search.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SupportTicketSerializer
    
    def get_queryset(self):
        queryset = SupportTicket.objects.select_related('created_by', 'assigned_to').all()
        
        # Filters
        status_filter = self.request.GET.get('status', None)
        priority_filter = self.request.GET.get('priority', None)
        search = self.request.GET.get('search', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        if search:
            queryset = queryset.filter(
                Q(ticket_id__icontains=search) |
                Q(subject__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SupportTicketDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a support ticket.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SupportTicketSerializer
    queryset = SupportTicket.objects.select_related('created_by', 'assigned_to').all()


class SupportTicketStatsView(APIView):
    """
    Get statistics for support tickets.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Check if user is admin
        if request.user.role != 'admin':
            return Response(
                {"detail": "Only administrators can access ticket statistics."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = SupportTicket.objects.aggregate(
            total_tickets=Count('id'),
            open_tickets=Count('id', filter=Q(status='open')),
            in_progress_tickets=Count('id', filter=Q(status='in_progress')),
            closed_tickets=Count('id', filter=Q(status='closed')),
            high_priority_tickets=Count('id', filter=Q(priority='high'))
        )
        
        serializer = SupportTicketStatsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)
