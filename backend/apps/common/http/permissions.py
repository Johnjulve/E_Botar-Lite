"""Custom permission classes for E-Botar Lite."""
from rest_framework import permissions


class IsSuperUser(permissions.BasePermission):
    """Allows access only to superusers (admin)."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser


class IsStaffOrSuperUser(permissions.BasePermission):
    """Allows access to staff or superusers."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or request.user.is_superuser
        )
