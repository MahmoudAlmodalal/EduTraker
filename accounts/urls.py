from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    PortalRegisterView,
    PortalLoginView,
    WorkstreamRegisterView,
    WorkstreamLoginView
)

# ============================================
# ADMIN & MANAGER PORTAL AUTH
# Base URL: /api/portal/auth/
# ============================================
portal_auth_patterns = [
    # Register - Creates user with role=GUEST
    # URL: /api/portal/auth/register/
    path('register/', PortalRegisterView.as_view(), name='portal_register'),
    
    # Login - Only ADMIN or MANAGER_WORKSTREAM allowed
    # URL: /api/portal/auth/login/
    path('login/', PortalLoginView.as_view(), name='portal_login'),
    
    # Token Refresh
    # URL: /api/portal/auth/token/refresh/
    path('token/refresh/', TokenRefreshView.as_view(), name='portal_token_refresh'),
]

# ============================================
# WORKSTREAM SPECIFIC AUTH
# Base URL: /api/workstream/<int:workstream_id>/auth/
# ============================================
workstream_auth_patterns = [
    # Register - Creates user with role=STUDENT, assigns to workstream
    # URL: /api/workstream/<workstream_id>/auth/register/
    path('register/', WorkstreamRegisterView.as_view(), name='workstream_register'),
    
    # Login - User MUST belong to this specific workstream
    # URL: /api/workstream/<workstream_id>/auth/login/
    path('login/', WorkstreamLoginView.as_view(), name='workstream_login'),
    
    # Token Refresh
    # URL: /api/workstream/<workstream_id>/auth/token/refresh/
    path('token/refresh/', TokenRefreshView.as_view(), name='workstream_token_refresh'),
]

# Default urlpatterns for include() - contains portal patterns
urlpatterns = portal_auth_patterns