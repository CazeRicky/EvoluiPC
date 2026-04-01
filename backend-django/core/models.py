from django.conf import settings
from django.db import models


class MachineSnapshot(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    schema_version = models.CharField(max_length=10, default="1.0")
    machine = models.JSONField(default=dict)
    diagnostics = models.JSONField(default=list)
    route = models.JSONField(default=list)
    catalog = models.JSONField(default=list)
    collected_at = models.DateTimeField(auto_now=True)
    source = models.CharField(max_length=50, default="desktop-agent")

    def __str__(self):
        return f"Snapshot<{self.user.username}>"
