# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0038_predictiontest_timedelta_back_in_granularity_increments'),
    ]

    operations = [
        migrations.AddField(
            model_name='trade',
            name='btc_amount',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='trade',
            name='btc_fee_amount',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='trade',
            name='fee_amount',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='trade',
            name='usd_amount',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='trade',
            name='usd_fee_amount',
            field=models.FloatField(null=True),
        ),
    ]
