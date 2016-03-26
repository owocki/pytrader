# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0045_auto_20160301_2047'),
    ]

    operations = [
        migrations.AddField(
            model_name='trade',
            name='net_profit',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='trade',
            name='opposite_price',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='trade',
            name='opposite_trade',
            field=models.ForeignKey(to='history.Trade', null=True),
        ),
        migrations.AddField(
            model_name='traderecommendation',
            name='trade',
            field=models.ForeignKey(to='history.Trade', null=True),
        ),
    ]
