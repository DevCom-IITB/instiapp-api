# Generated by Django 2.0.2 on 2018-03-24 06:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bodies", "0010_body_short_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="body",
            name="website_url",
            field=models.URLField(blank=True, null=True),
        ),
    ]
