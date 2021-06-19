from django.db import models
from rest_framework_api_key.models import AbstractAPIKey, BaseAPIKeyManager


class ProjectUserAPIKeyManager(BaseAPIKeyManager):
    def get_usable_keys(self):
        return super().get_usable_keys().filter(project__active=True)

class ProjectUser(models.Model):
    name = models.CharField(max_length=128, unique=True)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class ProjectUserAPIKey(AbstractAPIKey):
    project = models.ForeignKey(
        ProjectUser,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )
    
    objects = ProjectUserAPIKeyManager()

    @property
    def project_name(self):
        return self.project.name
    
    def __str__(self):
        return self.project.name

    class Meta(AbstractAPIKey.Meta):
        verbose_name = "Project-User API key"
        verbose_name_plural = "Project-User API keys"