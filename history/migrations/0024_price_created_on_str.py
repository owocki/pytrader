# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0023_balance_date_str'),
    ]

    operations = [
        migrations.AddField(
            model_name='price',
            name='created_on_str',
            field=models.CharField(default='', max_length=50),
        ),
    ]
