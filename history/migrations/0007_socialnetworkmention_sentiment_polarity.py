# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0006_auto_20160416_1305'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialnetworkmention',
            name='sentiment_polarity',
            field=models.FloatField(default=0.0),
        ),
    ]
