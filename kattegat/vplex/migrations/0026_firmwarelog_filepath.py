# Generated by Django 2.0.2 on 2018-04-05 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vplex', '0025_storage_array_connectivity'),
    ]

    operations = [
        migrations.AddField(
            model_name='firmwarelog',
            name='filepath',
            field=models.CharField(default='', max_length=500),
        ),
    ]