# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0011_auto_20160222_2043'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='predictiontest',
            name='biasstr',
        ),
        migrations.RemoveField(
            model_name='predictiontest',
            name='recurrentstr',
        ),
        migrations.AddField(
            model_name='predictiontest',
            name='bias_chart',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='predictiontest',
            name='recurrent_chart',
            field=models.IntegerField(default=-1),
        ),
    ]
