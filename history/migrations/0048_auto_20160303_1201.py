
from __future__ import unicode_literals

from django.db import models, migrations
from collections import Counter
from pprint import pprint
from django.core.management import call_command
from django.conf import settings
from history.models import Trade

def backfill_tradeprofitability(apps, schema_editor):
    for t in Trade.objects.filter(net_profit__isnull=False):
        t.calculate_profitability_exchange_rates()
        t.save()
    pass
    
class Migration(migrations.Migration):

    dependencies = [
        ('history', '0047_auto_20160303_1201'),
    ]

    operations = [
        migrations.RunPython(backfill_tradeprofitability),
    ]

