# Generated by Django 2.1 on 2018-10-01 14:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0005_newsentry_reacted_by"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="newsentry",
            index=models.Index(fields=["guid"], name="news_newsen_guid_2db5a2_idx"),
        ),
    ]
