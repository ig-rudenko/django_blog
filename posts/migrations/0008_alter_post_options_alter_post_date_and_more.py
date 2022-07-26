# Generated by Django 4.0.5 on 2022-07-30 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_post_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-date']},
        ),
        migrations.AlterField(
            model_name='post',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AddIndex(
            model_name='log',
            index=models.Index(fields=['datetime'], name='datetime_index'),
        ),
        migrations.AlterModelTable(
            name='log',
            table='posts_logs',
        ),
        migrations.AlterModelTable(
            name='profile',
            table='auth_user_profile',
        ),
    ]
