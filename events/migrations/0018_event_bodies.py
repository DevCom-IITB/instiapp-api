# Generated by Django 2.0.3 on 2018-03-29 07:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bodies", "0012_remove_body_events"),
        ("events", "0017_event_archived"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="bodies",
            field=models.ManyToManyField(
                blank=True, related_name="events", to="bodies.Body"
            ),
        ),
    ]
