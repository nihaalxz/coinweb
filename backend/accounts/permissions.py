from rest_framework import permissions

class IsAdminRole(permissions.BasePermission):
    """
    Allows access only to authenticated users with any administrative role.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, 'is_suspended', False):
            return False
        return user.is_admin_role

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or user.is_suspended:
            return False
        return user.role == 'SUPER_ADMIN' or user.is_superuser

class IsOperationsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or user.is_suspended:
            return False
        return user.role in ['SUPER_ADMIN', 'OPERATIONS_ADMIN'] or user.is_superuser

class IsFinanceAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or user.is_suspended:
            return False
        return user.role in ['SUPER_ADMIN', 'FINANCE_ADMIN'] or user.is_superuser

class IsSupportAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or user.is_suspended:
            return False
        return user.role in ['SUPER_ADMIN', 'OPERATIONS_ADMIN', 'SUPPORT_ADMIN'] or user.is_superuser

class IsMarketingAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or user.is_suspended:
            return False
        return user.role in ['SUPER_ADMIN', 'MARKETING_ADMIN', 'OPERATIONS_ADMIN'] or user.is_superuser
