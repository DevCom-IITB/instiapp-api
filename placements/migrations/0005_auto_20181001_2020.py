# Generated by Django 2.1 on 2018-10-01 14:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("placements", "0004_auto_20180408_1543"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="blogentry",
            index=models.Index(fields=["guid"], name="placements__guid_953b4f_idx"),
        ),
    ]
