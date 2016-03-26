# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0042_auto_20160227_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deposit',
            name='status',
            field=models.CharField(default='none', max_length=100),
        ),
    ]
