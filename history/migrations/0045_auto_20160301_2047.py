# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0044_classifiertest'),
    ]

    operations = [
        migrations.AddField(
            model_name='traderecommendation',
            name='clf',
            field=models.ForeignKey(to='history.ClassifierTest', null=True),
        ),
        migrations.AlterField(
            model_name='traderecommendation',
            name='made_by',
            field=models.ForeignKey(to='history.PredictionTest', null=True),
        ),
    ]
