# Generated by Django 3.1.2 on 2021-06-06 17:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0037_auto_20201101_1943"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="show_contact_no",
            field=models.BooleanField(default=False),
        ),
    ]
