# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import history.models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0027_auto_20160224_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balance',
            name='created_on',
            field=models.DateTimeField(default=history.models.get_time),
        ),
        migrations.AlterField(
            model_name='balance',
            name='modified_on',
            field=models.DateTimeField(default=history.models.get_time),
        ),
        migrations.AlterField(
            model_name='predictiontest',
            name='created_on',
            field=models.DateTimeField(default=history.models.get_time),
        ),
        migrations.AlterField(
            model_name='predictiontest',
            name='modified_on',
            field=models.DateTimeField(default=history.models.get_time),
        ),
        migrations.AlterField(
            model_name='price',
            name='created_on',
            field=models.DateTimeField(default=history.models.get_time),
        ),
        migrations.AlterField(
            model_name='price',
            name='modified_on',
            field=models.DateTimeField(default=history.models.get_time),
        ),
        migrations.AlterField(
            model_name='trade',
            name='created_on',
            field=models.DateTimeField(default=history.models.get_time),
        ),
        migrations.AlterField(
            model_name='trade',
            name='modified_on',
            field=models.DateTimeField(default=history.models.get_time),
        ),
        migrations.AlterField(
            model_name='traderecommendation',
            name='created_on',
            field=models.DateTimeField(default=history.models.get_time),
        ),
        migrations.AlterField(
            model_name='traderecommendation',
            name='modified_on',
            field=models.DateTimeField(default=history.models.get_time),
        ),
    ]
