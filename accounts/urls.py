from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views.portal_views import PortalRegisterView, PortalLoginView
from .views.workstream_portal_views import WorkstreamRegisterView, WorkstreamLoginView
from .views.user_views import (
    UserListApi,
    UserCreateApi,
    UserUpdateApi,
    UserDeactivateApi,
    UserActivateApi
)
from .views.configuration_views import SystemConfigurationListCreateView, SystemConfigurationDetailView

urlpatterns = [
    # Auth endpoints
    path('portal/auth/register/', PortalRegisterView.as_view(), name='portal-register'),
    path('portal/auth/login/', PortalLoginView.as_view(), name='portal-login'),
    
    path('workstream/<int:workstream_id>/auth/register/', WorkstreamRegisterView.as_view(), name='workstream-register'),
    path('workstream/<int:workstream_id>/auth/login/', WorkstreamLoginView.as_view(), name='workstream-login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    # User Management endpoints
    path('users/', UserListApi.as_view(), name='user-list'),
    path('users/create/', UserCreateApi.as_view(), name='user-create'),
    path('users/<int:user_id>/', UserUpdateApi.as_view(), name='user-update'),
    path('users/<int:user_id>/deactivate/', UserDeactivateApi.as_view(), name='user-deactivate'),
    path('users/<int:user_id>/activate/', UserActivateApi.as_view(), name='user-activate'),
    
    # System Configuration endpoints
    path('system-config/', SystemConfigurationListCreateView.as_view(), name='system-config-list'),
    path('system-config/<int:pk>/', SystemConfigurationDetailView.as_view(), name='system-config-detail'),
]