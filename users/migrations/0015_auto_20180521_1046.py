# Generated by Django 2.0.5 on 2018-05-21 05:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0014_auto_20180401_1314"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="year",
        ),
        migrations.AddField(
            model_name="userprofile",
            name="degree",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="department",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="department_name",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="graduation_year",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="join_year",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
