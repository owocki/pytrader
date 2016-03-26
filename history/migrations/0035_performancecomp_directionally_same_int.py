# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0034_auto_20160225_1040'),
    ]

    operations = [
        migrations.AddField(
            model_name='performancecomp',
            name='directionally_same_int',
            field=models.IntegerField(default=0),
        ),
    ]
