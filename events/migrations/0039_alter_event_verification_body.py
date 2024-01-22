# Generated by Django 3.2.16 on 2023-12-29 15:25

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0038_alter_event_verification_body"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="verification_body",
            field=multiselectfield.db.fields.MultiSelectField(
                choices=[
                    ("", "Institute Cultural Council"),
                    (
                        "06868e3e-773e-43d1-8bbb-efe17bb67ed1",
                        "Institute Technical Council",
                    ),
                    ("", "Institute Sports Council"),
                    ("", "Hostel Affairs"),
                ],
                max_length=39,
            ),
        ),
    ]