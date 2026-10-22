from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0046_remove_event_resubmitted_at"),
    ]

    operations = [
        migrations.CreateModel(
            name="EventEmail",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("message_id", models.CharField(max_length=998, unique=True)),
                (
                    "parent_message_id",
                    models.CharField(blank=True, max_length=998, null=True),
                ),
                ("recipients", models.JSONField(default=list)),
                ("to_recipients", models.JSONField(default=list)),
                ("cc_recipients", models.JSONField(default=list)),
                ("references", models.JSONField(default=list)),
                ("subject", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="emails",
                        to="events.event",
                    ),
                ),
            ],
            options={"ordering": ("created_at",)},
        ),
    ]
