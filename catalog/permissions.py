from rest_framework.permissions import BasePermission


class RolesPermissions(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.groups.filter(name="Admin").exists():
            return True
        if request.user.groups.filter(name="Manager").exists():
            if request.method == "DELETE":
                return False
            return True
        if request.user.groups.filter(name="Viewer").exists():
            return request.method in ["GET"]
        return False
