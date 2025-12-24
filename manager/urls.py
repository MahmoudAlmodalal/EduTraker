from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkStreamViewSet, SchoolViewSet, StaffCreationViewSet

router = DefaultRouter()
router.register(r'workstreams', WorkStreamViewSet, basename='workstream')
router.register(r'schools', SchoolViewSet, basename='school')

urlpatterns = [
    path('', include(router.urls)),
    path('create-staff/', StaffCreationViewSet.as_view({'post': 'create'}), name='create-staff'),
]