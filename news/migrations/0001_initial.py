# Generated by Django 2.0.5 on 2018-05-25 15:34

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("bodies", "0016_auto_20180404_2222"),
    ]

    operations = [
        migrations.CreateModel(
            name="NewsEntry",
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
                ("guid", models.CharField(blank=True, max_length=200)),
                ("title", models.CharField(blank=True, max_length=300)),
                ("content", models.TextField(blank=True)),
                ("link", models.CharField(blank=True, max_length=200)),
                ("published", models.DateTimeField(default=django.utils.timezone.now)),
                ("blog_url", models.URLField(null=True)),
                (
                    "body",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="bodies.Body"
                    ),
                ),
            ],
            options={
                "verbose_name": "News Entry",
                "verbose_name_plural": "News Entries",
                "ordering": ("-published",),
            },
        ),
    ]
