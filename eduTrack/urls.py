"""
URL configuration for eduTrack project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from accounts.urls import workstream_auth_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ============================================
    # AUTHENTICATION ENDPOINTS
    # ============================================
    
    # 1. Admin & Manager Portal Auth
    # Base URL: /api/portal/auth/
    # Endpoints:
    #   POST /api/portal/auth/register/  → Create user with role=GUEST
    #   POST /api/portal/auth/login/     → Login (ADMIN/MANAGER_WORKSTREAM only)
    #   POST /api/portal/auth/token/refresh/
    path('api/portal/auth/', include('accounts.urls')),
    
    # 2. Workstream Specific Auth
    # Base URL: /api/workstream/<int:workstream_id>/auth/
    # Endpoints:
    #   POST /api/workstream/<id>/auth/register/  → Create student, assign to workstream
    #   POST /api/workstream/<id>/auth/login/     → Login (must belong to workstream)
    #   POST /api/workstream/<id>/auth/token/refresh/
    path('api/workstream/<int:workstream_id>/auth/', include((workstream_auth_patterns, 'workstream_auth'))),
]
