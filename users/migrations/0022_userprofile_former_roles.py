# Generated by Django 2.0.7 on 2018-08-02 07:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("roles", "0008_auto_20180619_1855"),
        ("users", "0021_webpushsubscription"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="former_roles",
            field=models.ManyToManyField(
                blank=True, related_name="former_users", to="roles.BodyRole"
            ),
        ),
    ]
