# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import history.models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0039_auto_20160226_1028'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deposit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(default=history.models.get_time)),
                ('modified_on', models.DateTimeField(default=history.models.get_time)),
                ('symbol', models.CharField(max_length=30)),
                ('amount', models.FloatField(null=True)),
                ('type', models.CharField(max_length=10)),
                ('txid', models.CharField(default='', max_length=50)),
                ('status', models.CharField(default='none', max_length=10)),
                ('created_on_str', models.CharField(default='', max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
