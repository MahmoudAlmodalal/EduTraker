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
        return request.user.role == Role.WORKSTREAM_MANAGER

class IsSchoolManager(permissions.BasePermission):
    """
    Allows access to School Managers, Workstream Managers.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == Role.SCHOOL_MANAGER

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
