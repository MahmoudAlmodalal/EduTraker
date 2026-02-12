from rest_framework import generics, permissions, filters
from drf_spectacular.utils import extend_schema, OpenApiParameter
from ..models import LessonPlan, Teacher
from ..serializers.lesson_plan_serializers import LessonPlanSerializer
from accounts.models import Role
from reports.utils import log_activity

class IsLessonPlanAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of a lesson plan to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.teacher.user == request.user or request.user.role == Role.ADMIN

@extend_schema(
    tags=['Teacher - Lesson Plans'],
    summary='List and create lesson plans',
    parameters=[
        OpenApiParameter(name='course', type=int, description='Filter by course ID'),
        OpenApiParameter(name='classroom', type=int, description='Filter by classroom ID'),
        OpenApiParameter(name='academic_year', type=int, description='Filter by academic year ID'),
    ]
)
class LessonPlanListCreateAPIView(generics.ListCreateAPIView):
    """
    List all lesson plans or create a new one.
    Teachers can only create lesson plans for themselves.
    """
    serializer_class = LessonPlanSerializer
    permission_classes = [permissions.IsAuthenticated, IsLessonPlanAuthorOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content', 'objectives']

    def get_queryset(self):
        queryset = LessonPlan.objects.all()
        course_id = self.request.query_params.get('course')
        classroom_id = self.request.query_params.get('classroom')
        academic_year_id = self.request.query_params.get('academic_year')

        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if classroom_id:
            queryset = queryset.filter(classroom_id=classroom_id)
        if academic_year_id:
            queryset = queryset.filter(academic_year_id=academic_year_id)

        # Non-teachers/admins can only see published lesson plans
        if self.request.user.role not in [Role.TEACHER, Role.ADMIN]:
            queryset = queryset.filter(is_published=True)
        
        return queryset

    def perform_create(self, serializer):
        teacher = Teacher.objects.get(user=self.request.user)
        lesson_plan = serializer.save(teacher=teacher)
        log_activity(
            actor=self.request.user,
            action_type='CREATE',
            entity_type='LessonPlan',
            entity_id=lesson_plan.id,
            description=f"Created lesson plan '{lesson_plan.title}'.",
            request=self.request
        )

@extend_schema(
    tags=['Teacher - Lesson Plans'],
    summary='Retrieve, update or delete a lesson plan'
)
class LessonPlanRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a lesson plan instance.
    """
    queryset = LessonPlan.objects.all()
    serializer_class = LessonPlanSerializer
    permission_classes = [permissions.IsAuthenticated, IsLessonPlanAuthorOrReadOnly]

    def perform_update(self, serializer):
        lesson_plan = serializer.save()
        log_activity(
            actor=self.request.user,
            action_type='UPDATE',
            entity_type='LessonPlan',
            entity_id=lesson_plan.id,
            description=f"Updated lesson plan '{lesson_plan.title}'.",
            request=self.request
        )

    def perform_destroy(self, instance):
        title = instance.title
        lesson_plan_id = instance.id
        super().perform_destroy(instance)
        log_activity(
            actor=self.request.user,
            action_type='DELETE',
            entity_type='LessonPlan',
            entity_id=lesson_plan_id,
            description=f"Deleted lesson plan '{title}'.",
            request=self.request
        )
