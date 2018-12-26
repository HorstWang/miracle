# Generated by Django 2.0.1 on 2018-01-28 01:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vplex', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CDLog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('investigation_id', models.IntegerField()),
                ('serial_number', models.CharField(max_length=100)),
                ('date_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='FirmwareLog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('cdlog_id', models.IntegerField()),
                ('text', models.CharField(max_length=5000)),
                ('ip', models.CharField(default='N/A', max_length=100)),
                ('director', models.CharField(default='N/A', max_length=50)),
                ('year', models.IntegerField(default=-1)),
                ('month', models.IntegerField(default=-1)),
                ('day', models.IntegerField(default=-1)),
                ('hour', models.IntegerField(default=-1)),
                ('minute', models.IntegerField(default=-1)),
                ('second', models.IntegerField(default=-1)),
                ('date_time', models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0))),
                ('component', models.CharField(default='N/A', max_length=30)),
                ('event_id', models.IntegerField(default=-1)),
                ('i_port_name', models.CharField(default='N/A', max_length=100)),
                ('i_port', models.CharField(default='N/A', max_length=100)),
                ('t_port_name', models.CharField(default='N/A', max_length=100)),
                ('t_port', models.CharField(default='N/A', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='FirmwareLogEventCode',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('version', models.CharField(default='N/A', max_length=50)),
                ('component', models.CharField(default='N/A', max_length=50)),
                ('code', models.IntegerField(default=-1)),
                ('internalRCA', models.CharField(default='N/A', max_length=3000)),
                ('customerRCA', models.CharField(default='N/A', max_length=3000)),
                ('customerDescription', models.CharField(default='N/A', max_length=3000)),
                ('formatString', models.CharField(default='N/A', max_length=3000)),
            ],
        ),
        migrations.RenameField(
            model_name='investigation',
            old_name='datetime',
            new_name='date_time',
        ),
    ]