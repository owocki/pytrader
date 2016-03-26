# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0040_deposit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deposit',
            name='txid',
            field=models.CharField(default='', max_length=500),
        ),
    ]
