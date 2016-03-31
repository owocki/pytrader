# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import history.models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balance',
            name='created_on',
            field=models.DateTimeField(default=history.models.get_time, db_index=True),
        ),
        migrations.AlterField(
            model_name='balance',
            name='date_str',
            field=models.CharField(default='0', max_length=20, db_index=True),
        ),
        migrations.AlterField(
            model_name='classifiertest',
            name='type',
            field=models.CharField(default='mock', max_length=30, db_index=True),
        ),
        migrations.AlterField(
            model_name='deposit',
            name='created_on',
            field=models.DateTimeField(default=history.models.get_time, db_index=True),
        ),
        migrations.AlterField(
            model_name='performancecomp',
            name='created_on',
            field=models.DateTimeField(default=history.models.get_time, db_index=True),
        ),
        migrations.AlterField(
            model_name='performancecomp',
            name='price_timerange_end',
            field=models.DateTimeField(default=None, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='performancecomp',
            name='price_timerange_start',
            field=models.DateTimeField(default=None, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='predictiontest',
            name='type',
            field=models.CharField(default='mock', max_length=30, db_index=True),
        ),
        migrations.AlterField(
            model_name='price',
            name='created_on',
            field=models.DateTimeField(default=history.models.get_time, db_index=True),
        ),
        migrations.AlterField(
            model_name='price',
            name='symbol',
            field=models.CharField(max_length=30, db_index=True),
        ),
        migrations.AlterField(
            model_name='trade',
            name='created_on',
            field=models.DateTimeField(default=history.models.get_time, db_index=True),
        ),
        migrations.AlterField(
            model_name='traderecommendation',
            name='created_on',
            field=models.DateTimeField(default=history.models.get_time, db_index=True),
        ),
    ]
