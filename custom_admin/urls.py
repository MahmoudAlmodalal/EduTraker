from django.urls import path
from custom_admin.views import (
    SupportTicketListCreateView,
    SupportTicketDetailView,
    SupportTicketStatsView
)

app_name = 'custom_admin'

urlpatterns = [
    path('support-tickets/', SupportTicketListCreateView.as_view(), name='support-ticket-list'),
    path('support-tickets/<int:pk>/', SupportTicketDetailView.as_view(), name='support-ticket-detail'),
    path('support-tickets/stats/', SupportTicketStatsView.as_view(), name='support-ticket-stats'),
]
