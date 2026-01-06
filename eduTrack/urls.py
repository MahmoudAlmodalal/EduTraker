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
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ============================================
    # API DOCUMENTATION (Swagger/OpenAPI)
    # ============================================
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # ============================================
    # AUTHENTICATION ENDPOINTS
    # ============================================
    
    # All auth endpoints are defined in accounts.urls with full prefixes:
    # /api/portal/auth/...
    # /api/workstream/<id>/auth/...
    path('api/', include('accounts.urls')),
    path('api/', include('workstream.urls')),
    path('api/', include('reports.urls')),
    path('api/manager/', include('manager.urls')),
    path('api/manager/', include('student.urls')),
    path('api/custom-admin/', include('custom_admin.urls')),
    path('api/workstream-manager/', include('workstream_manager.urls')),
    path('api/teacher/', include('teacher.urls')),
    path('api/guardian/', include('guardian.urls')),
    path('api/user-messages/', include('user_messages.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/secretary/', include('secretary.urls')),
]

