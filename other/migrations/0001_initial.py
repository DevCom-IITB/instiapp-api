# Generated by Django 2.1.5 on 2019-01-23 06:01

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("users", "0027_auto_20181003_1609"),
        ("sessions", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Device",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("time_of_creation", models.DateTimeField(auto_now_add=True)),
                ("last_ping", models.DateTimeField()),
                ("fcm_id", models.CharField(blank=True, max_length=200, null=True)),
                ("application", models.CharField(blank=True, max_length=50)),
                ("app_version", models.CharField(blank=True, max_length=50)),
                ("platform", models.CharField(blank=True, max_length=50)),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="devices",
                        to="sessions.Session",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="devices",
                        to="users.UserProfile",
                    ),
                ),
            ],
        ),
    ]
