# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0003_auto_20160330_1920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balance',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='balance',
            name='modified_on',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='classifiertest',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='classifiertest',
            name='modified_on',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='deposit',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='deposit',
            name='modified_on',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='performancecomp',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='performancecomp',
            name='modified_on',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='predictiontest',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='predictiontest',
            name='modified_on',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='price',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='price',
            name='modified_on',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='trade',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='trade',
            name='modified_on',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='traderecommendation',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='traderecommendation',
            name='modified_on',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
