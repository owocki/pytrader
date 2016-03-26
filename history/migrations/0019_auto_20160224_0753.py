# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0018_auto_20160224_0749'),
    ]

    operations = [
        migrations.AlterField(
            model_name='predictiontest',
            name='avg_diff',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='predictiontest',
            name='percent_correct',
            field=models.FloatField(null=True),
        ),
    ]
