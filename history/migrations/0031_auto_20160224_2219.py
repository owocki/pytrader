from __future__ import unicode_literals

from django.db import models, migrations
from collections import Counter
from pprint import pprint
from django.core.management import call_command
from django.conf import settings
from history.models import TradeRecommendation
import datetime

def backfill_messagetype(apps, schema_editor):
    for p in TradeRecommendation.objects.filter(created_on_str='').all():
        p.created_on_str = (p.created_on - datetime.timedelta(hours=int(7))).strftime('%Y-%m-%d %H:%M')
        p.net_amount = -1 if p.recommendation == 'SELL' else ( 1 if p.recommendation == 'BUY' else 0 )
        p.save()
    
class Migration(migrations.Migration):

    dependencies = [
        ('history', '0030_auto_20160224_2219'),
    ]

    operations = [
        migrations.RunPython(backfill_messagetype),
    ]

