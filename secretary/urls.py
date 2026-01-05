from django.urls import path
from secretary.views import (
    SecretaryListApi,
    SecretaryCreateApi,
    SecretaryDetailApi,
    SecretaryDeactivateApi,
)

app_name = 'secretary'

urlpatterns = [
    # Secretary endpoints
    path('', SecretaryListApi.as_view(), name='secretary-list'),
    path('create/', SecretaryCreateApi.as_view(), name='secretary-create'),
    path('<int:secretary_id>/', SecretaryDetailApi.as_view(), name='secretary-detail'),
    path('<int:secretary_id>/deactivate/', SecretaryDeactivateApi.as_view(), name='secretary-deactivate'),
]
