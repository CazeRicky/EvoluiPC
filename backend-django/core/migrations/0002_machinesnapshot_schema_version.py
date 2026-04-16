from django.db import migrations, models


# Migração adiciona versão do schema.
class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        # Adiciona campo schema_version.
        migrations.AddField(
            model_name="machinesnapshot",
            name="schema_version",
            field=models.CharField(default="1.0", max_length=10),
        ),
    ]
