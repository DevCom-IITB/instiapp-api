# Generated by Django 3.2.16 on 2023-07-22 13:35

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0042_userprofile_followed_communities"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="community_roles",
        ),
    ]
