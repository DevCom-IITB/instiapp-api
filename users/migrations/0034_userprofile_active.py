# Generated by Django 2.2.3 on 2019-07-21 20:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0033_userprofile_last_ping"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="active",
            field=models.BooleanField(default=True),
        ),
    ]
