# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0003_auto_20160330_1920'),
    ]

    operations = [
        migrations.AddField(
            model_name='predictiontest',
            name='evaluation_error',
            field=models.FloatField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='predictiontest',
            name='training_error',
            field=models.FloatField(default=0, null=True),
        ),
    ]
