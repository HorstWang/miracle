# Generated by Django 2.1.1 on 2018-10-01 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vplex', '0032_vvperflog'),
    ]

    operations = [
        migrations.CreateModel(
            name='tach_sh_login',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('cdlog_id', models.IntegerField()),
                ('engine_name', models.CharField(default='N/A', max_length=100)),
                ('director_name', models.CharField(default='N/A', max_length=100)),
                ('i', models.CharField(default='N/A', max_length=50)),
                ('t', models.CharField(default='N/A', max_length=50)),
            ],
        ),
    ]