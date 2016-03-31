# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0002_auto_20160330_1854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classifiertest',
            name='symbol',
            field=models.CharField(max_length=30, db_index=True),
        ),
        migrations.AlterField(
            model_name='predictiontest',
            name='symbol',
            field=models.CharField(max_length=30, db_index=True),
        ),
    ]
