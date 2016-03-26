# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0035_performancecomp_directionally_same_int'),
    ]

    operations = [
        migrations.AddField(
            model_name='performancecomp',
            name='price_timerange_end',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='performancecomp',
            name='price_timerange_start',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='performancecomp',
            name='tr_timerange_start',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
