# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0017_auto_20160224_0741'),
    ]

    operations = [
        migrations.CreateModel(
            name='TradeRecommendation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('symbol', models.CharField(max_length=30)),
                ('made_on', models.TextField(max_length=30)),
                ('recommendation', models.CharField(max_length=30)),
                ('confidence', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='predictiontest',
            name='type',
            field=models.CharField(default='mock', max_length=30),
        ),
        migrations.AddField(
            model_name='traderecommendation',
            name='made_by',
            field=models.ForeignKey(to='history.PredictionTest'),
        ),
    ]
