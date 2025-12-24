from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TeacherViewSet, CourseViewSet, ClassRoomViewSet, 
    CourseAllocationViewSet, AssignmentViewSet, MarkViewSet, 
    AttendanceViewSet
)

router = DefaultRouter()
router.register(r'profiles', TeacherViewSet)
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'classrooms', ClassRoomViewSet, basename='classroom')
router.register(r'allocations', CourseAllocationViewSet, basename='allocation')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'marks', MarkViewSet, basename='mark')
router.register(r'attendance', AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('', include(router.urls)),
]