# Generated by Django 3.1.4 on 2021-01-27 09:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_auto_20210127_0955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='convert',
            name='in_tmstmp',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 1, 27, 9, 56, 30, 581145)),
        ),
        migrations.AlterField(
            model_name='convert',
            name='out_tmstmp',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 1, 27, 9, 56, 30, 581162)),
        ),
    ]
