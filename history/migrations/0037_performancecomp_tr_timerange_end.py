# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0036_auto_20160225_1335'),
    ]

    operations = [
        migrations.AddField(
            model_name='performancecomp',
            name='tr_timerange_end',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
