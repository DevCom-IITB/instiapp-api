# Generated by Django 2.0.5 on 2018-06-01 06:11

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0019_auto_20180523_2158"),
        ("news", "0003_auto_20180525_2231"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserNewsReaction",
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
                ("reaction", models.IntegerField(default=0)),
                (
                    "news",
                    models.ForeignKey(
                        default=uuid.uuid4,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="unr",
                        to="news.NewsEntry",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        default=uuid.uuid4,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="unr",
                        to="users.UserProfile",
                    ),
                ),
            ],
            options={
                "verbose_name": "User-News Reaction",
                "verbose_name_plural": "User-News Reactions",
            },
        ),
    ]
