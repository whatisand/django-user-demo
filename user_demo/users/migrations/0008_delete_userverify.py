# Generated by Django 4.0.3 on 2022-03-25 09:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0007_rename_verified_userverify_is_used_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="UserVerify",
        ),
    ]
