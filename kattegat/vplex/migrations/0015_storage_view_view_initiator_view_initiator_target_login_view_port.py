# Generated by Django 2.0.2 on 2018-02-12 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vplex', '0014_director_port_sfps'),
    ]

    operations = [
        migrations.CreateModel(
            name='storage_view',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('cdlog_id', models.IntegerField()),
                ('name', models.CharField(default='N/A', max_length=50)),
                ('staus', models.CharField(default='N/A', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='view_initiator',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='N/A', max_length=50)),
                ('wwnn', models.CharField(default='N/A', max_length=100)),
                ('wwpn', models.CharField(default='N/A', max_length=100)),
                ('host_type', models.CharField(default='N/A', max_length=100)),
                ('logged_in', models.CharField(default='N/A', max_length=100)),
                ('cross_connected', models.CharField(default='N/A', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='view_initiator_target_login',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('view_initiator_id', models.IntegerField()),
                ('view_port_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='view_port',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('port_id', models.IntegerField()),
            ],
        ),
    ]
