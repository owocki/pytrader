# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0029_trade_created_on_str'),
    ]

    operations = [
        migrations.AddField(
            model_name='traderecommendation',
            name='created_on_str',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AddField(
            model_name='traderecommendation',
            name='net_amount',
            field=models.FloatField(default=0),
        ),
    ]
