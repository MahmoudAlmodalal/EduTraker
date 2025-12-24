from rest_framework import viewsets, permissions
from .models import Guardian, GuardianStudentLink
from .serializers import GuardianSerializer, GuardianStudentLinkSerializer
from accounts.permissions import IsSchoolManager, IsSecretary

class GuardianViewSet(viewsets.ModelViewSet):
    """
    API for managing Guardians.
    """
    serializer_class = GuardianSerializer
    permission_classes = [IsSchoolManager | IsSecretary]

    def get_queryset(self):
        # Return all guardians linked to students in the user's school
        user = self.request.user
        if user.school:
            return Guardian.objects.filter(children__school=user.school).distinct()
        return Guardian.objects.none()

class GuardianLinkViewSet(viewsets.ModelViewSet):
    """
    API for linking Guardians to Students.
    """
    serializer_class = GuardianStudentLinkSerializer
    permission_classes = [IsSchoolManager | IsSecretary]
    queryset = GuardianStudentLink.objects.all()