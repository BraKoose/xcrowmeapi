from rest_framework.permissions import BasePermission

from .models import User

class IsAuthenticatedAdmin(BasePermission):
    def has_permission(self, request, view):
        # Get the user, if the user is staff or admin (open access)
        if request.user.is_authenticated:
            user = User.objects.get(pk=request.user.pk)
            if user.staff or user.admin:
                return True
        return False