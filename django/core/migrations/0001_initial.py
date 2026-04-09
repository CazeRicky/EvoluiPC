from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


# Migração inicial das tabelas core.
class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Cria tabela de snapshots.
        migrations.CreateModel(
            name="MachineSnapshot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("machine", models.JSONField(default=dict)),
                ("diagnostics", models.JSONField(default=list)),
                ("route", models.JSONField(default=list)),
                ("catalog", models.JSONField(default=list)),
                ("collected_at", models.DateTimeField(auto_now=True)),
                ("source", models.CharField(default="desktop-agent", max_length=50)),
                (
                    "user",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
    ]
