# Generated by Django 2.0.1 on 2018-02-05 04:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vplex', '0010_auto_20180201_0409'),
    ]

    operations = [
        migrations.AddField(
            model_name='firmwarelog',
            name='cluster',
            field=models.CharField(default='N/A', max_length=30),
        ),
    ]
