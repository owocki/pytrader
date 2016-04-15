# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0004_auto_20160409_1213'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='balance',
            name='date_str',
        ),
        migrations.RemoveField(
            model_name='deposit',
            name='created_on_str',
        ),
        migrations.RemoveField(
            model_name='performancecomp',
            name='created_on_str',
        ),
        migrations.RemoveField(
            model_name='price',
            name='created_on_str',
        ),
        migrations.RemoveField(
            model_name='trade',
            name='created_on_str',
        ),
        migrations.RemoveField(
            model_name='traderecommendation',
            name='created_on_str',
        ),
    ]
