# Generated by Django 3.2.9 on 2022-01-05 11:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drawpage', '0004_alter_log_log_file'),
    ]

    operations = [
        migrations.RenameField(
            model_name='log',
            old_name='log_file',
            new_name='log',
        ),
    ]
