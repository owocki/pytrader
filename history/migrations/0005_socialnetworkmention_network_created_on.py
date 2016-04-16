# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import history.models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0004_socialnetworkmention'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialnetworkmention',
            name='network_created_on',
            field=models.DateTimeField(default=history.models.get_time),
        ),
    ]
