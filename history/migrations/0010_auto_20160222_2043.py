# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0009_predictiontest_recurrent'),
    ]

    operations = [
        migrations.AddField(
            model_name='predictiontest',
            name='biasstr',
            field=models.CharField(default='Null', max_length=10),
        ),
        migrations.AddField(
            model_name='predictiontest',
            name='recurrentstr',
            field=models.CharField(default='Null', max_length=10),
        ),
    ]
