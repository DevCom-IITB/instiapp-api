# Generated by Django 2.0.2 on 2018-03-03 11:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("locations", "0004_auto_20180303_1640"),
        ("events", "0007_auto_20180221_1718"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="event",
            name="venue",
        ),
        migrations.AddField(
            model_name="event",
            name="venues",
            field=models.ManyToManyField(
                related_name="events", to="locations.Location"
            ),
        ),
    ]
