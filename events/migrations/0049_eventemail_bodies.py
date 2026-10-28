from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0048_alter_eventemail_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="eventemail",
            name="body_text",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="eventemail",
            name="body_html",
            field=models.TextField(blank=True, default=""),
        ),
    ]