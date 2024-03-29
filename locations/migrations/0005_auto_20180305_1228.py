# Generated by Django 2.0.2 on 2018-03-05 06:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("locations", "0004_auto_20180303_1640"),
    ]

    operations = [
        migrations.AlterField(
            model_name="location",
            name="lat",
            field=models.DecimalField(
                blank=True, decimal_places=6, max_digits=9, null=True
            ),
        ),
        migrations.AlterField(
            model_name="location",
            name="lng",
            field=models.DecimalField(
                blank=True, decimal_places=6, max_digits=9, null=True
            ),
        ),
    ]
