# Generated by Django 2.0.1 on 2018-02-01 04:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vplex', '0009_auto_20180201_0136'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cdlog',
            old_name='dump_succeed',
            new_name='dump_succeeded',
        ),
    ]
