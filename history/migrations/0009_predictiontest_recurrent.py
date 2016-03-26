# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0008_auto_20160222_1821'),
    ]

    operations = [
        migrations.AddField(
            model_name='predictiontest',
            name='recurrent',
            field=models.BooleanField(default=False),
        ),
    ]
