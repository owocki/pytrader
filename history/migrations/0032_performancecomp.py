# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import history.models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0031_auto_20160224_2219'),
    ]

    operations = [
        migrations.CreateModel(
            name='PerformanceComp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(default=history.models.get_time)),
                ('modified_on', models.DateTimeField(default=history.models.get_time)),
                ('symbol', models.CharField(max_length=30)),
                ('nn_rec', models.FloatField()),
                ('actual_movement', models.FloatField()),
                ('delta', models.FloatField()),
                ('created_on_str', models.CharField(max_length=30)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
