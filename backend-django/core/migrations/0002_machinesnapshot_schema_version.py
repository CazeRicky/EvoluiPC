from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="machinesnapshot",
            name="schema_version",
            field=models.CharField(default="1.0", max_length=10),
        ),
    ]
