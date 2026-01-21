from django.urls import path

from notifications.views.notification_views import (
    NotificationListApi,
    NotificationMarkReadApi,
    NotificationDetailApi,
)

app_name = 'notifications'

urlpatterns = [
    path('', NotificationListApi.as_view(), name='notification-list'),
    path('<int:pk>/', NotificationDetailApi.as_view(), name='notification-detail'),
    path('<int:pk>/mark-read/', NotificationMarkReadApi.as_view(), name='notification-mark-read'),
]
