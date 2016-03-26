# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0025_auto_20160224_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='trade',
            name='net_amount',
            field=models.FloatField(null=True),
        ),
    ]
