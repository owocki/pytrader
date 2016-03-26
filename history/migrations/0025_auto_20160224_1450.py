
from __future__ import unicode_literals

from django.db import models, migrations
from collections import Counter
from pprint import pprint
from django.core.management import call_command
from django.conf import settings
from history.models import Price

def backfill_messagetype(apps, schema_editor):
    for p in Price.objects.filter(created_on_str='').all():
        p.created_on_str = str(p.created_on)
        p.save()
    
class Migration(migrations.Migration):

    dependencies = [
        ('history', '0024_price_created_on_str'),
    ]

    operations = [
        migrations.RunPython(backfill_messagetype),
    ]

