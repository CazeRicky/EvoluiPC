from django.db import models


# Snapshot salvo da maquina do usuario.
class MachineSnapshot(models.Model):
    user_id = models.PositiveIntegerField(unique=True)
    schema_version = models.CharField(max_length=10, default="1.0")
    machine = models.JSONField(default=dict)
    diagnostics = models.JSONField(default=list)
    route = models.JSONField(default=list)
    catalog = models.JSONField(default=list)
    collected_at = models.DateTimeField(auto_now=True)
    source = models.CharField(max_length=50, default="desktop-agent")

    def __str__(self):
        # Exibe o identificador do usuario no admin.
        return f"Snapshot<{self.user_id}>"
