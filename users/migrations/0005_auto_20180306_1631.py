# Generated by Django 2.0.2 on 2018-03-06 11:01

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_auto_20180305_1239"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="userprofile",
            options={"verbose_name": "Profile", "verbose_name_plural": "Profiles"},
        ),
    ]
