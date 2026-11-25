from rest_framework.permissions import BasePermission


class UserPermission(BasePermission):
    """
    Checks permission based on Role -> Permissions.
    Admin (superuser) has all permissions.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Admin has full access
        if user.is_superuser:
            return True

        # Permission required by API
        permission_codename = getattr(view, "permission_codename", None)

        # If API doesn't specify a permission, allow authenticated users
        if not permission_codename:
            return True

        # Staff permission check
        if hasattr(user, "staff_profile"):
            return user.staff_profile.role.permissions.filter(
                codename=permission_codename,
                is_active=True
            ).exists()

        # Student permission check
        if hasattr(user, "student_profile"):
            return user.student_profile.role.permissions.filter(
                codename=permission_codename,
                is_active=True
            ).exists()

        return False