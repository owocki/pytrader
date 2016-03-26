# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0022_auto_20160224_1113'),
    ]

    operations = [
        migrations.AddField(
            model_name='balance',
            name='date_str',
            field=models.CharField(default='0', max_length=20),
        ),
    ]
