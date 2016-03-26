
from __future__ import unicode_literals

from django.db import models, migrations
from collections import Counter
from pprint import pprint
from django.core.management import call_command
from django.conf import settings
from history.models import PredictionTest


def backfill_messagetype(apps, schema_editor):
    for pt in PredictionTest.objects.all():
        pt.bias_chart =  -1 if pt.bias is None else ( 1 if pt.bias else 0 )
        pt.recurrent_chart = -1 if pt.recurrent is None else ( 1 if pt.recurrent else 0 )
        pt.save()

class Migration(migrations.Migration):

    dependencies = [
        ('history', '0012_auto_20160222_2046'),
    ]

    operations = [
        migrations.RunPython(backfill_messagetype),
    ]

