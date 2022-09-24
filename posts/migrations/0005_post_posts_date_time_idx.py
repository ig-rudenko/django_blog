# Generated by Django 4.0.5 on 2022-07-18 13:44

from django.db import migrations, models
from django.contrib.postgres.operations import AddIndexConcurrently


class Migration(migrations.Migration):
    atomic = False
    dependencies = [
        ('posts', '0004_alter_log_message'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['date'], name='posts_date_time_idx'),
        ),
    ]
