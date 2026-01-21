from rest_framework import generics, filters, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from teacher.models import LearningMaterial
from teacher.serializers import LearningMaterialSerializer
from accounts.models import Role

class  IsMaterialManagerOrReadOnly(permissions.BasePermission):
    """
    Custom permission:
    - Teacher: Create, Update, Delete (own materials).
    - Student/Guardian/Manager: Read only.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
             return True
        # Write permissions only for Teachers (and maybe Admins)
        return request.user.role in [Role.TEACHER, Role.ADMIN]

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True # Logic to restrict reading to enrolled students can be added here or via queryset
        
        # Write: only owner or admin
        return obj.uploaded_by == request.user or request.user.role == Role.ADMIN

@extend_schema(
    tags=['Teacher - Learning Materials'],
    summary='List and create learning materials',
    description='List learning materials filtered by course, classroom, or academic year. Teachers can upload new materials.',
    parameters=[
        OpenApiParameter(name='course', type=int, description='Filter by course ID'),
        OpenApiParameter(name='classroom', type=int, description='Filter by classroom ID'),
        OpenApiParameter(name='academic_year', type=int, description='Filter by academic year ID'),
        OpenApiParameter(name='search', type=str, description='Search by title or description'),
    ],
    responses={
        200: LearningMaterialSerializer(many=True),
        201: LearningMaterialSerializer,
    }
)
class LearningMaterialListCreateView(generics.ListCreateAPIView):
    """
    List and Create Learning Materials.
    """
    serializer_class = LearningMaterialSerializer
    permission_classes = [IsMaterialManagerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']

    def get_queryset(self):
        user = self.request.user
        queryset = LearningMaterial.objects.all()
        
        # Role-based filtering
        if user.role == Role.ADMIN:
            pass # Admin sees all
        elif user.role == Role.MANAGER_WORKSTREAM:
            queryset = queryset.filter(academic_year__school__work_stream_id=user.work_stream_id)
        elif user.role == Role.MANAGER_SCHOOL:
            queryset = queryset.filter(academic_year__school_id=user.school_id)
        elif user.role == Role.TEACHER:
            # Teachers see materials in their school, or maybe only their own?
            # SRS says "Teachers can upload... List filtered...". Let's assume they see all in school.
            queryset = queryset.filter(academic_year__school_id=user.school_id)
        elif user.role == Role.STUDENT:
            # Students see materials for classrooms they are enrolled in
            from student.models import StudentEnrollment
            enrolled_classroom_ids = StudentEnrollment.objects.filter(
                student__user_id=user.id,
                status__in=['active', 'enrolled']
            ).values_list('class_room_id', flat=True)
            queryset = queryset.filter(classroom_id__in=enrolled_classroom_ids)
        elif user.role == Role.GUARDIAN:
            # Guardians see materials for their children's classrooms
            from guardian.models import GuardianStudent
            child_ids = GuardianStudent.objects.filter(guardian__user_id=user.id).values_list('student_id', flat=True)
            from student.models import StudentEnrollment
            enrolled_classroom_ids = StudentEnrollment.objects.filter(
                student_id__in=child_ids,
                status__in=['active', 'enrolled']
            ).values_list('class_room_id', flat=True)
            queryset = queryset.filter(classroom_id__in=enrolled_classroom_ids)
        else:
            queryset = queryset.none()

        # Manual filtering since django_filters is not available
        course_id = self.request.query_params.get('course')
        classroom_id = self.request.query_params.get('classroom')
        academic_year_id = self.request.query_params.get('academic_year')
        
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if classroom_id:
            queryset = queryset.filter(classroom_id=classroom_id)
        if academic_year_id:
            queryset = queryset.filter(academic_year_id=academic_year_id)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

@extend_schema(
    tags=['Teacher - Learning Materials'],
    summary='Retrieve, update or delete learning material',
    description='Manage a specific learning material. Teachers can only manage their own materials.',
    responses={
        200: LearningMaterialSerializer,
        204: OpenApiResponse(description='Deleted successfully'),
    }
)
class LearningMaterialDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, Update, and Delete Learning Materials.
    """
    queryset = LearningMaterial.objects.all()
    serializer_class = LearningMaterialSerializer
    permission_classes = [IsMaterialManagerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']
