# Generated by Django 3.1.4 on 2021-01-09 10:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='convert',
            name='in_tmstmp',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='convert',
            name='out_tmstmp',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now),
        ),
    ]
