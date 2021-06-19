from django.contrib import admin
from rest_framework_api_key.admin import APIKeyModelAdmin

from .models import ProjectUser, ProjectUserAPIKey

@admin.register(ProjectUserAPIKey)
class ProjectAPIKeyModelAdmin(APIKeyModelAdmin):
    list_display = [*APIKeyModelAdmin.list_display, "project_name"]
    search_fields = [*APIKeyModelAdmin.search_fields, "project_name"]

admin.site.register(ProjectUser)