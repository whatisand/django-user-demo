# Generated by Django 4.0.3 on 2022-03-21 16:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_rename_email_user_username'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='username',
            new_name='email',
        ),
    ]
