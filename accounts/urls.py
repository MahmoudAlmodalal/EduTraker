from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomTokenObtainPairView, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("api/auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/", include(router.urls)),
]