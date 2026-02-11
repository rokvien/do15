from rest_framework.permissions import BasePermission


class RoleBasedPermission(BasePermission):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        # Admin — полный доступ
        if request.user.groups.filter(name="Admin").exists():
            return True

        # Viewer — только GET
        if request.user.groups.filter(name="Viewer").exists():
            return request.method in ["GET", "HEAD", "OPTIONS"]

        # Manager — CRUD без удаления
        if request.user.groups.filter(name="Manager").exists():
            if request.method == "DELETE":
                return False
            return True

        return False


