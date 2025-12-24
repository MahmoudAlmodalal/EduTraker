from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    GuestRegistrationView,
    WorkstreamStudentRegistrationView,
    ManagementLoginView,
    WorkstreamLoginView
)

urlpatterns = [
    # --- Registration Endpoints ---
    
    # 1. Admin/Guest Registration
    # URL: /api/accounts/register/admin/
    path('register/admin/', GuestRegistrationView.as_view(), name='register_guest'),

    # 2. Workstream/Student Registration
    # URL: /api/accounts/register/<workstream_name>/
    # Example: /api/accounts/register/Engineering/
    path('register/<str:workstream_name>/', WorkstreamStudentRegistrationView.as_view(), name='register_student'),


    # --- Login Endpoints ---

    # 1. Management Login (Super Admin & Workstream Managers)
    # URL: /api/accounts/login/admin/
    path('login/admin/', ManagementLoginView.as_view(), name='login_admin'),

    # 2. Workstream User Login (Teachers, Students, School Managers)
    # URL: /api/accounts/login/<workstream_name>/
    # Example: /api/accounts/login/Engineering/
    path('login/<str:workstream_name>/', WorkstreamLoginView.as_view(), name='login_workstream'),

    # --- Token Refresh (Standard for all users) ---
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]