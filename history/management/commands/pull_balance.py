from django.core.management.base import BaseCommand
from django.conf import settings
from history.tools import get_exchange_rate_to_btc, get_exchange_rate_btc_to_usd, get_deposit_balance
from history.models import Balance, Trade
import datetime
from django.db import transaction

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)


class Command(BaseCommand):

    help = 'pulls balances and stores them in a DB'

    def handle(self, *args, **options):
        from history.poloniex import poloniex

        # hit API
        poo = poloniex(settings.API_KEY, settings.API_SECRET)
        balances = poo.returnBalances()

        # record balances
        deposited_amount_btc, deposited_amount_usd = get_deposit_balance()
        with transaction.atomic():
            for ticker in balances:
                val = float(balances[ticker]['available']) + float(balances[ticker]['onOrders'])
                if val > 0.0001:

                    exchange_rate_coin_to_btc = get_exchange_rate_to_btc(ticker)
                    exchange_rate_btc_to_usd = get_exchange_rate_btc_to_usd()
                    btc_val = exchange_rate_coin_to_btc * val
                    usd_val = exchange_rate_btc_to_usd * btc_val
                    b = Balance(symbol=ticker, coin_balance=val, btc_balance=btc_val,
                                exchange_to_btc_rate=exchange_rate_coin_to_btc, usd_balance=usd_val,
                                exchange_to_usd_rate=exchange_rate_coin_to_btc,
                                deposited_amount_btc=deposited_amount_btc if ticker == 'BTC' else 0.00,
                                deposited_amount_usd=deposited_amount_usd if ticker == 'BTC' else 0.00)
                    b.save()

        for b in Balance.objects.filter(date_str='0'):
            # django timezone stuff , FML
            b.date_str = datetime.datetime.strftime(b.created_on - datetime.timedelta(hours=int(7)), '%Y-%m-%d %H:%M')
            b.save()

        # normalize trade recommendations too.  merp
        for tr in Trade.objects.filter(created_on_str=''):
            # django timezone stuff , FML
            tr.created_on_str = datetime.datetime.strftime(
                tr.created_on - datetime.timedelta(hours=int(7)), '%Y-%m-%d %H:%M')
            tr.save()
