# Generated by Django 3.2.16 on 2023-07-22 13:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0043_remove_userprofile_community_roles'),
        ('roles', '0020_communityrole'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CommunityRole',
        ),
    ]