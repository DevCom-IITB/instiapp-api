# Generated by Django 2.1 on 2018-10-02 19:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bodies", "0022_auto_20180925_2228"),
    ]

    operations = [
        migrations.AddField(
            model_name="body",
            name="canonical_name",
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
