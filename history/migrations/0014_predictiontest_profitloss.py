# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0013_auto_20160222_2046'),
    ]

    operations = [
        migrations.AddField(
            model_name='predictiontest',
            name='profitloss',
            field=models.FloatField(default=0),
        ),
    ]
