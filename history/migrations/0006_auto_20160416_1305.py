# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0005_socialnetworkmention_network_created_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialnetworkmention',
            name='network_id',
            field=models.CharField(default=0, max_length=100, db_index=True),
        ),
    ]
