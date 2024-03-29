# Generated by Django 2.0.2 on 2018-03-05 06:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bodies", "0006_remove_body_followers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="body",
            name="description",
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name="body",
            name="events",
            field=models.ManyToManyField(
                blank=True, null=True, related_name="bodies", to="events.Event"
            ),
        ),
    ]
