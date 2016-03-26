# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0021_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='balance',
            name='exchange_to_usd_rate',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='balance',
            name='usd_balance',
            field=models.FloatField(null=True),
        ),
    ]
