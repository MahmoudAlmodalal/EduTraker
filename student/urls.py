from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, StudentEnrollmentViewSet

router = DefaultRouter()
router.register(r'profiles', StudentViewSet, basename='student')
router.register(r'enrollments', StudentEnrollmentViewSet, basename='enrollment')

urlpatterns = [
    path('', include(router.urls)),
]