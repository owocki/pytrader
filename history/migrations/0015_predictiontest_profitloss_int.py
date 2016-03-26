# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0014_predictiontest_profitloss'),
    ]

    operations = [
        migrations.AddField(
            model_name='predictiontest',
            name='profitloss_int',
            field=models.IntegerField(default=0),
        ),
    ]
