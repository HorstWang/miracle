# Generated by Django 2.0.1 on 2018-02-01 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vplex', '0008_auto_20180201_0024'),
    ]

    operations = [
        migrations.AddField(
            model_name='cdlog',
            name='download_completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cdlog',
            name='dump_completed',
            field=models.BooleanField(default=False),
        ),
    ]
