# Generated by Django 2.0.2 on 2018-03-06 11:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0013_auto_20180306_1631"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="followers",
            field=models.ManyToManyField(
                blank=True,
                related_name="following_events",
                through="events.UserEventStatus",
                to="users.UserProfile",
            ),
        ),
    ]
