from rest_framework_api_key.permissions import BaseHasAPIKey
from .models import ProjectUserAPIKey

class HasProjectAPIKey(BaseHasAPIKey):
    model = ProjectUserAPIKey 

class HasStaffProjectAPIKey(BaseHasAPIKey):
    model = ProjectUserAPIKey

    def has_permission(self, request, view):
        val = super().has_permission(request, view)
        if val:
            key = self.get_key(request)
            api_key = self.model.objects.get_from_key(key)

            return (api_key.project.staff or api_key.project.admin)
        return False