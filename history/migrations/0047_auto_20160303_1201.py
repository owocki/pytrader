# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0046_auto_20160302_2135'),
    ]

    operations = [
        migrations.AddField(
            model_name='trade',
            name='btc_net_profit',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='trade',
            name='usd_net_profit',
            field=models.FloatField(null=True),
        ),
    ]
