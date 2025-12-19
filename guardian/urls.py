from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GuardianViewSet, GuardianLinkViewSet

router = DefaultRouter()
router.register(r'profiles', GuardianViewSet, basename='guardian')
router.register(r'links', GuardianLinkViewSet, basename='guardian-link')

urlpatterns = [
    path('', include(router.urls)),
]