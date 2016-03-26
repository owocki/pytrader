# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0037_performancecomp_tr_timerange_end'),
    ]

    operations = [
        migrations.AddField(
            model_name='predictiontest',
            name='timedelta_back_in_granularity_increments',
            field=models.IntegerField(default=0),
        ),
    ]
