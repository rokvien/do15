from django.views.generic import DeleteView
from rest_framework.permissions import BasePermission


class RoleBasedPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.groups.filter(name="Admin").exists():
            return True
        if request.user.groups.filter(name="Viewer").exists():
            return request.method in ["GET"]
        if request.user.groups.filter(name="Manager").exists():
            if request.method == "DELETE":
                return False
            return True
        return False


