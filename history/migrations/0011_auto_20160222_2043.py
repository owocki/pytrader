
from __future__ import unicode_literals

from django.db import models, migrations
from collections import Counter
from pprint import pprint
from django.core.management import call_command
from django.conf import settings
from history.models import PredictionTest

def backfill_messagetype(apps, schema_editor):
    pass
    
class Migration(migrations.Migration):

    dependencies = [
        ('history', '0010_auto_20160222_2043'),
    ]

    operations = [
        migrations.RunPython(backfill_messagetype),
    ]

