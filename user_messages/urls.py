from django.urls import path
from user_messages.views import (
    MessageListCreateView,
    MessageDetailView,
    MessageThreadView,
    MessageReadView
)

app_name = 'user_messages'

urlpatterns = [
    path('', MessageListCreateView.as_view(), name='message-list-create'),
    path('<int:pk>/', MessageDetailView.as_view(), name='message-detail'),
    path('<int:pk>/read/', MessageReadView.as_view(), name='message-mark-read'),
    path('threads/<uuid:thread_id>/', MessageThreadView.as_view(), name='message-thread'),
]
