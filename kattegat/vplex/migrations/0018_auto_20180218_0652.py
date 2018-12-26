# Generated by Django 2.0.2 on 2018-02-18 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vplex', '0017_cdlog_code_level'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cdlog',
            old_name='serial_number',
            new_name='hardware_type',
        ),
        migrations.AddField(
            model_name='cdlog',
            name='product_type',
            field=models.CharField(default='N/A', max_length=100),
        ),
    ]
