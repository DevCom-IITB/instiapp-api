# Generated by Django 2.1 on 2018-09-30 08:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0024_event_time_of_modification"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="starting_notified",
            field=models.BooleanField(default=False),
        ),
    ]
