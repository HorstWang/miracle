# Generated by Django 2.0.2 on 2018-02-21 00:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vplex', '0022_auto_20180221_0019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='view_port',
            name='port_id',
            field=models.IntegerField(default=-1),
        ),
    ]
