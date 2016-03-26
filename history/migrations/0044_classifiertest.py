# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import history.models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0043_auto_20160227_1147'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassifierTest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(default=history.models.get_time)),
                ('modified_on', models.DateTimeField(default=history.models.get_time)),
                ('type', models.CharField(default='mock', max_length=30)),
                ('symbol', models.CharField(max_length=30)),
                ('name', models.CharField(default='', max_length=100)),
                ('datasetinputs', models.IntegerField()),
                ('granularity', models.IntegerField()),
                ('minutes_back', models.IntegerField(default=0)),
                ('timedelta_back_in_granularity_increments', models.IntegerField(default=0)),
                ('time', models.IntegerField(default=0)),
                ('prediction_size', models.IntegerField(default=0)),
                ('score', models.IntegerField(default=0)),
                ('output', models.TextField()),
                ('percent_correct', models.FloatField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
