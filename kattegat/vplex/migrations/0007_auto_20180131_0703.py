# Generated by Django 2.0.1 on 2018-01-31 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vplex', '0006_auto_20180131_0655'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cdlog',
            old_name='downloaded_succeed',
            new_name='download_started',
        ),
        migrations.AddField(
            model_name='cdlog',
            name='download_succeeded',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cdlog',
            name='exception',
            field=models.CharField(default='N/A', max_length=3000),
        ),
    ]
