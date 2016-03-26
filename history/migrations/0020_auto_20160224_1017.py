# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0019_auto_20160224_0753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='orderNumber',
            field=models.CharField(default='', max_length=50),
        ),
    ]
