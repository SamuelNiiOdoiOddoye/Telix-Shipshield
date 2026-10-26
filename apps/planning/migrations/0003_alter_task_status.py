from django.db import migrations, models


def normalize_in_progress_status(apps, schema_editor):
    Task = apps.get_model("planning", "Task")
    Task.objects.filter(status="in_progresss").update(status="in_progress")


class Migration(migrations.Migration):

    dependencies = [("planning", "0002_projectplan")]

    operations = [
        migrations.RunPython(normalize_in_progress_status, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="task",
            name="status",
            field=models.CharField(
                choices=[
                    ("todo", "To do"),
                    ("in_progress", "In progress"),
                    ("blocked", "Blocked"),
                    ("done", "Done"),
                ],
                default="todo",
                max_length=20,
            ),
        ),
    ]
