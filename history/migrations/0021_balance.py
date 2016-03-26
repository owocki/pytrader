# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0020_auto_20160224_1017'),
    ]

    operations = [
        migrations.CreateModel(
            name='Balance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('symbol', models.CharField(max_length=30)),
                ('coin_balance', models.FloatField()),
                ('btc_balance', models.FloatField()),
                ('exchange_to_btc_rate', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
