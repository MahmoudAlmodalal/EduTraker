from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse, OpenApiTypes
from reports.services.export_service import ExportService
from accounts.permissions import IsStaffUser

from reports.services.report_generation_services import ReportGenerationService
from reports.utils import log_activity

class ReportExportView(APIView):
    """
    Export reports to Excel, CSV, or PDF.
    """
    permission_classes = [IsStaffUser]

    @extend_schema(
        tags=['Reports & Statistics', 'Exports'],
        summary='Export reports to multiple formats',
        # ... (rest of the schema remains the same)
        description='Generate and download a report in Excel, CSV, or PDF format. Supports generic data or specific report types like "student_performance" or "attendance".',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'report_type': {'type': 'string', 'enum': ['generic', 'student_performance', 'attendance', 'student_list', 'comprehensive_academic', 'system_usage']},
                    'export_format': {'type': 'string', 'enum': ['excel', 'csv', 'pdf'], 'default': 'excel'},
                    'data': {
                        'type': 'array', 
                        'items': {'type': 'object'},
                        'description': 'Optional raw data to export (for generic type)'
                    }
                },
                'required': ['report_type']
            }
        },
        responses={
            200: OpenApiResponse(description='File binary stream', response=OpenApiTypes.BINARY),
            400: OpenApiResponse(description='Invalid parameters or no data'),
            403: OpenApiResponse(description='Permission denied')
        },
        examples=[
            OpenApiExample(
                'Export Student Performance as PDF',
                value={'report_type': 'student_performance', 'export_format': 'pdf'},
                request_only=True
            ),
             OpenApiExample(
                'Export Generic Data as CSV',
                value={
                    'report_type': 'generic',
                    'export_format': 'csv',
                    'data': [{'col1': 'val1', 'col2': 'val2'}]
                },
                request_only=True
            )
        ]
    )
    def post(self, request):
        report_type = request.data.get("report_type", "generic")
        export_format = request.data.get("export_format") or request.data.get("format") or "excel"
        export_format = export_format.lower()
        
        # Safely get school_id. Super Admins might not have a school_id attribute depending on the User model implementation.
        school_id = getattr(request.user, 'school_id', None)

        if report_type == "student_performance":
            data = ReportGenerationService.get_student_performance_data(school_id=school_id)
            headers = ["student", "grade", "gpa"]
        elif report_type == "attendance":
            data = ReportGenerationService.get_attendance_report(school_id=school_id)
            headers = ["student", "date", "status", "course"]
        elif report_type == "student_list":
            data = ReportGenerationService.get_student_list(school_id=school_id)
            headers = ["name", "email", "id", "status"]
        elif report_type == "comprehensive_academic":
            data = ReportGenerationService.get_comprehensive_academic_data(school_id=school_id, actor=request.user)
            headers = ["category", "workstream", "count", "schools", "metric", "school_name", "students", "teachers"]
        elif report_type == "system_usage":
            data = ReportGenerationService.get_comprehensive_system_usage_data(school_id=school_id, actor=request.user)
            headers = ["category", "workstream", "teacher_count", "metric", "value", "description"]
        else:
            # Check if data provided (generic export)
            data = request.data.get("data", [])
            if not data:
                return Response({"detail": "No data to export or invalid report type."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Safely extract headers from first dict in list
            headers = []
            if data and isinstance(data, list) and isinstance(data[0], dict):
                headers = list(data[0].keys())
            else:
                # If it's not a list of dicts, it's invalid for generic export
                return Response({"detail": "Data must be a list of dictionaries for generic export."}, status=status.HTTP_400_BAD_REQUEST)

        if not data:
            # We still proceed to generate an empty file with headers
            pass

        # Log the export activity
        log_activity(
            actor=request.user,
            action_type='EXPORT',
            entity_type='Report',
            description=f"Exported {report_type} report as {export_format}",
            request=request
        )

        if export_format == "csv":
            return ExportService.export_to_csv(data, headers, filename=report_type)
        elif export_format == "pdf":
            return ExportService.export_to_pdf(data, headers, filename=report_type)
        else:
            return ExportService.export_to_excel(data, headers, filename=report_type)
