# Generated by Django 2.0.2 on 2018-02-12 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vplex', '0013_auto_20180205_1524'),
    ]

    operations = [
        migrations.CreateModel(
            name='director',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('cdlog_id', models.IntegerField()),
                ('name', models.CharField(default='N/A', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='port',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('director_id', models.IntegerField()),
                ('name', models.CharField(default='N/A', max_length=30)),
                ('address', models.CharField(default='N/A', max_length=100)),
                ('role', models.CharField(default='N/A', max_length=50)),
                ('status', models.CharField(default='N/A', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='sfps',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('port_id', models.IntegerField()),
                ('name', models.CharField(default='N/A', max_length=30)),
                ('manufacturer', models.CharField(default='N/A', max_length=50)),
                ('part_number', models.CharField(default='N/A', max_length=50)),
                ('serial_number', models.CharField(default='N/A', max_length=50)),
                ('rx_power', models.IntegerField(null=True)),
                ('tx_power', models.IntegerField(null=True)),
                ('temprature', models.IntegerField(null=True)),
            ],
        ),
    ]
