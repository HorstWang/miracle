# Generated by Django 2.0.2 on 2018-03-18 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vplex', '0023_auto_20180221_0019'),
    ]

    operations = [
        migrations.CreateModel(
            name='storage_array',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('cdlog_id', models.IntegerField(default=-1)),
                ('name', models.CharField(default='N/A', max_length=50)),
                ('vendor', models.CharField(default='N/A', max_length=30)),
                ('revision', models.CharField(default='N/A', max_length=30)),
            ],
        ),
    ]
