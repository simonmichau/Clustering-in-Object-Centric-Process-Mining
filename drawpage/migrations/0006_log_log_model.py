# Generated by Django 3.2.9 on 2022-01-05 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drawpage', '0005_rename_log_file_log_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='log_model',
            field=models.BinaryField(default=None, null=True),
        ),
    ]
