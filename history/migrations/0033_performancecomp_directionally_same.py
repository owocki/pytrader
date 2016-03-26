# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0032_performancecomp'),
    ]

    operations = [
        migrations.AddField(
            model_name='performancecomp',
            name='directionally_same',
            field=models.BooleanField(default=False),
        ),
    ]
