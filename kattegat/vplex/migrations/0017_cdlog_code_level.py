# Generated by Django 2.0.2 on 2018-02-15 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vplex', '0016_auto_20180213_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='cdlog',
            name='code_level',
            field=models.CharField(default='N/A', max_length=100),
        ),
    ]