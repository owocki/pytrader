# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import history.models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0003_auto_20160330_1920'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialNetworkMention',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(default=history.models.get_time)),
                ('modified_on', models.DateTimeField(default=history.models.get_time)),
                ('network_name', models.CharField(max_length=30, db_index=True)),
                ('network_username', models.CharField(max_length=100)),
                ('network_id', models.BigIntegerField(default=0)),
                ('symbol', models.CharField(max_length=30, db_index=True)),
                ('text', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
