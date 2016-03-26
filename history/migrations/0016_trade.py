# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0015_predictiontest_profitloss_int'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('symbol', models.CharField(max_length=30)),
                ('price', models.FloatField()),
                ('amount', models.FloatField(null=True)),
                ('type', models.CharField(max_length=10)),
                ('response', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
