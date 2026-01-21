from rest_framework import permissions
from .models import Role

class IsSuperAdmin(permissions.BasePermission):
    """
    Allows access only to Super Admins.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.ADMIN

class IsWorkStreamManager(permissions.BasePermission):
    """
    Allows access to Workstream Managers and Admins.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == Role.MANAGER_WORKSTREAM

class IsSchoolManager(permissions.BasePermission):
    """
    Allows access to School Managers, Workstream Managers.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == Role.MANAGER_SCHOOL

class IsTeacher(permissions.BasePermission):
    """
    Allows access to Teachers.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.TEACHER

class IsSecretary(permissions.BasePermission):
    """
    Allows access to Registrars/Secretaries.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.SECRETARY

class IsStudent(permissions.BasePermission):
    """
    Allows access to Students.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.STUDENT

class IsGuardian(permissions.BasePermission):
    """
    Allows access to Guardians.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.GUARDIAN

class IsAdminOrManager(permissions.BasePermission):
    """
    Allows access to Admins, Workstream Managers, and School Managers.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL]
class IsStaffUser(permissions.BasePermission):
    """
    Allows access to Staff Users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL,Role.TEACHER,Role.SECRETARY]
class IsAdminOrManagerOrSecretary(permissions.BasePermission):
    """
    Allows access to Admins, Managers, and Secretaries.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL,Role.SECRETARY] 
class IsAdminOrManagerWorkstream(permissions.BasePermission):
    """
    Allows access to Admins and Workstream Managers.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [Role.ADMIN, Role.MANAGER_WORKSTREAM]

class IsConfigManager(permissions.BasePermission):
    """
    Custom permission for System Configuration access.
    - Admin: Full access to everything.
    - Workstream Manager: Manage own WS configs, Read Global.
    - School Manager: Manage own School configs, Read Global/WS.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL
        ]

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == Role.ADMIN:
            return True
        
        if user.role == Role.MANAGER_WORKSTREAM:
            # Can manage own workstream configs
            if obj.work_stream == user.work_stream and obj.school is None:
                return True
            # Can read global or own workstream's school configs (if we allowed that, but standard is managing heirarchy)
            # Re-reading requirement: "Workstream Manager... School Manager"
            # Let's say WS Manager can read Global, Own WS, and Own WS's Schools.
            # But can only EDIT Own WS configs.
            if request.method in permissions.SAFE_METHODS:
                # Read access logic
                if obj.school:
                    return obj.school.work_stream == user.work_stream
                if obj.work_stream:
                    return obj.work_stream == user.work_stream
                return True # Global
            return False

        if user.role == Role.MANAGER_SCHOOL:
            # Can manage own school configs
            if obj.school == user.school:
                return True
            # Read access: Global, Own WS, Own School
            if request.method in permissions.SAFE_METHODS:
                if obj.school:
                    return obj.school == user.school
                if obj.work_stream:
                    return obj.work_stream == user.school.work_stream
                return True # Global
            return False
            
        return False
