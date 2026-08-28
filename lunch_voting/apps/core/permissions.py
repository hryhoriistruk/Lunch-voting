"""Role-based permissions shared across apps.

Keeping these in one place (instead of re-checking ``request.user.role``
inline in every view) means the access rules are declared once and read
the same way everywhere.
"""
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Allows access only to staff/admin accounts.

    Admins manage restaurants, menus and employee accounts.
    """

    message = "Only admin users can perform this action."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_admin)


class IsEmployee(BasePermission):
    """Allows access only to employee accounts (the voting users)."""

    message = "Only employee users can perform this action."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_employee)
