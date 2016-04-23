# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0008_auto_20160416_1920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialnetworkmention',
            name='network_created_on',
            field=models.DateTimeField(),
        ),
    ]
