
from __future__ import unicode_literals

from django.db import models, migrations
from collections import Counter
from pprint import pprint
from django.core.management import call_command
from django.conf import settings
from history.models import Trade

def backfill_messagetype(apps, schema_editor):
    for t in Trade.objects.all():
        t.net_amount=((1 if t.type == 'buy' else -1 ) * t.amount)
        t.save()
    
class Migration(migrations.Migration):

    dependencies = [
        ('history', '0026_trade_net_amount'),
    ]

    operations = [
        migrations.RunPython(backfill_messagetype),
    ]
