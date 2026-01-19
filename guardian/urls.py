from django.urls import path

from guardian.views.guardian_views import (
    GuardianListApi,
    GuardianCreateApi,
    GuardianDetailApi,
    GuardianDeactivateApi,
    GuardianActivateApi,
    GuardianStudentLinkApi,
)

app_name = 'guardian'

urlpatterns = [
    path('guardians/', GuardianListApi.as_view(), name='guardian-list'),
    path('guardians/create/', GuardianCreateApi.as_view(), name='guardian-create'),
    path('guardians/<int:guardian_id>/', GuardianDetailApi.as_view(), name='guardian-detail'),
    path('guardians/<int:guardian_id>/deactivate/', GuardianDeactivateApi.as_view(), name='guardian-deactivate'),
    path('guardians/<int:guardian_id>/activate/', GuardianActivateApi.as_view(), name='guardian-activate'),
    
    path('guardians/<int:guardian_id>/students/', GuardianStudentLinkApi.as_view(), name='guardian-student-link'),
]
