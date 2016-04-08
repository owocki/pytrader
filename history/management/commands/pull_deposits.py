from django.core.management.base import BaseCommand
from django.conf import settings
import datetime
from history.tools import get_utc_unixtime
from history.models import Deposit


class Command(BaseCommand):

    help = 'pulls balances and stores them in a DB'

    def handle(self, *args, **options):
        from history.poloniex import poloniex

        poo = poloniex(settings.API_KEY, settings.API_SECRET)
        now = get_utc_unixtime()
        r = poo.returnDepositHistory(0, now)
        deposits = r['deposits'] + r['withdrawals']
        for d in deposits:
            print(d)
            currency = d['currency']
            amount = float(d['amount']) * (-1 if 'withdrawalNumber' in d.keys() else 1)
            timestamp = d['timestamp']
            txid = d['withdrawalNumber'] if 'withdrawalNumber' in d.keys() else d['txid']
            status = d['status']
            created_on = datetime.datetime.fromtimestamp(timestamp)
            try:
                d = Deposit.objects.get(txid=txid)
            except:
                d = Deposit()
            d.symbol = currency
            d.amount = amount
            d.txid = txid
            d.type = 'deposit' if amount > 0 else 'withdrawal'
            d.status = status
            d.created_on = created_on
            d.modified_on = created_on
            d.created_on_str = datetime.datetime.strftime(
                created_on - datetime.timedelta(hours=int(7)), '%Y-%m-%d %H:%M')
            d.save()
