# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0007_predictiontest_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='price',
            name='highestbid',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='price',
            name='lowestask',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='price',
            name='volume',
            field=models.FloatField(null=True),
        ),
    ]
