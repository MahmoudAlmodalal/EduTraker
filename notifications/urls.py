from django.urls import path

from notifications.views.notification_views import (
    NotificationListApi,
    NotificationMarkReadApi,
    NotificationDetailApi,
    NotificationMarkAllReadApi,
    NotificationUnreadCountApi,
)

app_name = 'notifications'

urlpatterns = [
    path('', NotificationListApi.as_view(), name='notification-list'),
    path('unread-count/', NotificationUnreadCountApi.as_view(), name='notification-unread-count'),
    path('mark-all-read/', NotificationMarkAllReadApi.as_view(), name='notification-mark-all-read'),
    path('<int:pk>/', NotificationDetailApi.as_view(), name='notification-detail'),
    path('<int:pk>/mark-read/', NotificationMarkReadApi.as_view(), name='notification-mark-read'),
]
