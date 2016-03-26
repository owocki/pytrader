# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0016_trade'),
    ]

    operations = [
        migrations.AddField(
            model_name='trade',
            name='orderNumber',
            field=models.CharField(default='', max_length=10),
        ),
        migrations.AddField(
            model_name='trade',
            name='status',
            field=models.CharField(default='none', max_length=10),
        ),
    ]
