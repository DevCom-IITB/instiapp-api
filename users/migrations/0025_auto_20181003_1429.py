# Generated by Django 2.1 on 2018-10-03 08:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0024_auto_20180930_1352"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserTag",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "target",
                    models.CharField(
                        choices=[
                            ("roll_no", "Roll No"),
                            ("department", "Department"),
                            ("degree", "Degree"),
                            ("join_year", "Join Year"),
                            ("graduation_year", "Graduation Year"),
                            ("hostel", "Hostel"),
                            ("room", "Room"),
                            ("android_version", "Android Version"),
                        ],
                        max_length=40,
                    ),
                ),
                ("regex", models.CharField(max_length=150)),
                (
                    "secondary_target",
                    models.CharField(
                        choices=[
                            ("roll_no", "Roll No"),
                            ("department", "Department"),
                            ("degree", "Degree"),
                            ("join_year", "Join Year"),
                            ("graduation_year", "Graduation Year"),
                            ("hostel", "Hostel"),
                            ("room", "Room"),
                            ("android_version", "Android Version"),
                        ],
                        max_length=40,
                    ),
                ),
                ("secondary_regex", models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name="UserTagCategory",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=30)),
            ],
        ),
        migrations.AddField(
            model_name="usertag",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="users.UserTagCategory"
            ),
        ),
    ]
