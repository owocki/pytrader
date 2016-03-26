# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0041_auto_20160227_1134'),
    ]

    operations = [
        migrations.AddField(
            model_name='balance',
            name='deposited_amount_btc',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='balance',
            name='deposited_amount_usd',
            field=models.FloatField(default=0.0),
        ),
    ]
