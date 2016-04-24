# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0007_socialnetworkmention_sentiment_polarity'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialnetworkmention',
            name='sentiment_subjectivity',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='socialnetworkmention',
            name='network_created_on',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
