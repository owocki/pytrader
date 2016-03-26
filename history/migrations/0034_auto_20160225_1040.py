# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0033_performancecomp_directionally_same'),
    ]

    operations = [
        migrations.AddField(
            model_name='performancecomp',
            name='pct_buy',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='performancecomp',
            name='pct_hold',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='performancecomp',
            name='pct_sell',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='performancecomp',
            name='rec_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='performancecomp',
            name='weighted_avg_nn_rec',
            field=models.FloatField(default=0),
        ),
    ]
