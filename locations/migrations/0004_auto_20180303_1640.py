# Generated by Django 2.0.2 on 2018-03-03 11:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("locations", "0003_auto_20180217_2231"),
    ]

    operations = [
        migrations.AlterField(
            model_name="location",
            name="lat",
            field=models.DecimalField(decimal_places=6, max_digits=9),
        ),
        migrations.AlterField(
            model_name="location",
            name="lng",
            field=models.DecimalField(decimal_places=6, max_digits=9),
        ),
    ]
