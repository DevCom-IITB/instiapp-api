# Generated by Django 2.0.2 on 2018-03-19 07:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("roles", "0002_auto_20180319_1258"),
        ("users", "0009_userprofile_roles"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="institute_roles",
            field=models.ManyToManyField(
                blank=True, related_name="users", to="roles.InstituteRole"
            ),
        ),
    ]
