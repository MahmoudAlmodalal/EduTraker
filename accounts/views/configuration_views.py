from rest_framework import generics, serializers, filters
from rest_framework.permissions import IsAuthenticated
from ..models import SystemConfiguration, Role
from ..serializers import SystemConfigurationSerializer
from ..permissions import IsConfigManager
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

@extend_schema(
    tags=['System Configuration'],
    summary='List and create configurations',
    description='List all system configurations or create a new one. Filterable by scope, school, and workstream.',
    parameters=[
        OpenApiParameter(name='school', type=int, description='Filter by school ID'),
        OpenApiParameter(name='work_stream', type=int, description='Filter by workstream ID'),
        OpenApiParameter(name='scope', type=str, enum=['global', 'workstream', 'school'], description='Filter by scope'),
        OpenApiParameter(name='search', type=str, description='Search by config key'),
    ],
    responses={
        200: SystemConfigurationSerializer(many=True),
        201: SystemConfigurationSerializer,
    }
)
class SystemConfigurationListCreateView(generics.ListCreateAPIView):
    """
    List and Create System Configurations.
    """
    serializer_class = SystemConfigurationSerializer
    permission_classes = [IsConfigManager]
    filter_backends = [filters.SearchFilter]
    search_fields = ['config_key']

    def get_queryset(self):
        user = self.request.user
        queryset = SystemConfiguration.objects.all()
        
        # Filtering by params
        school_id = self.request.query_params.get('school')
        work_stream_id = self.request.query_params.get('work_stream')
        scope = self.request.query_params.get('scope') # global, workstream, school

        # Base filtering access
        if user.role == Role.ADMIN:
            pass # Admin sees all
        elif user.role == Role.MANAGER_WORKSTREAM:
            # See Global + Own WS + Own WS's Schools
            queryset = queryset.filter(
                Q(school__isnull=True, work_stream__isnull=True) |
                Q(work_stream=user.work_stream) |
                Q(school__work_stream=user.work_stream)
            )
        elif user.role == Role.MANAGER_SCHOOL:
            # See Global + Own WS (parent) + Own School
            queryset = queryset.filter(
                Q(school__isnull=True, work_stream__isnull=True) |
                Q(work_stream=user.school.work_stream) |
                Q(school=user.school)
            )
        else:
             # Fallback for others (teachers, students generally don't access this API directly via this view, 
             # but if permission allowed, show only relevant)
             return SystemConfiguration.objects.none()

        # Apply specific filters if requested
        if scope == 'global':
             queryset = queryset.filter(school__isnull=True, work_stream__isnull=True)
        elif scope == 'workstream':
             queryset = queryset.filter(work_stream__isnull=False)
        elif scope == 'school':
             queryset = queryset.filter(school__isnull=False)

        if school_id:
             queryset = queryset.filter(school_id=school_id)
        if work_stream_id:
             queryset = queryset.filter(work_stream_id=work_stream_id)
             
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        save_kwargs = {}
        
        if user.role == Role.MANAGER_SCHOOL:
            # Force school scope
            save_kwargs['school'] = user.school
            if serializer.validated_data.get('work_stream'):
                 raise serializers.ValidationError("School Managers cannot set Workstream configurations.")
        elif user.role == Role.MANAGER_WORKSTREAM:
            # Force workstream scope
            save_kwargs['work_stream'] = user.work_stream
            if serializer.validated_data.get('school'):
                 raise serializers.ValidationError("Workstream Managers cannot directly set School configurations via generic create (use specific endpoints or admin).")
        elif user.role == Role.ADMIN:
            # Admin can set whatever they pass in payload, default to global if nothing passed
            pass
            
        serializer.save(**save_kwargs)

@extend_schema(
    tags=['System Configuration'],
    summary='Retrieve, update or delete configuration',
    description='Manage a specific system configuration.',
    responses={
        200: SystemConfigurationSerializer,
        204: OpenApiResponse(description='Deleted successfully'),
    }
)
class SystemConfigurationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, Update, and Delete System Configurations.
    """
    queryset = SystemConfiguration.objects.all()
    serializer_class = SystemConfigurationSerializer
    permission_classes = [IsConfigManager]
