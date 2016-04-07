from django.core.management.base import BaseCommand
from django.conf import settings
from history.models import Trade
from history.tools import print_and_log
import datetime

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)


class Command(BaseCommand):

    help = 'executes scheduled  trades'

    def handle(self, *args, **options):
        from history.poloniex import poloniex
        from history.models import Price
        import time

        poo = poloniex(settings.API_KEY, settings.API_SECRET)

        if settings.MAKE_TRADES:
            time.sleep(40)

        for t in Trade.objects.filter(created_on__lt=datetime.datetime.now(), status='scheduled'):

            # bid right below the lowest ask, or right above the highest bid so that our orders get filled
            action = t.type
            price = Price.objects.filter(symbol=t.symbol).order_by('-created_on').first()
            if action == 'sell':
                rate = price.lowestask * 0.999
            else:
                rate = price.highestbid * 1.001

            t.price = rate

            if action == 'buy':
                try:
                    response = {} if not settings.MAKE_TRADES else poo.buy(t.symbol, rate, t.amount)
                except Exception as e:
                    print_and_log('(st)act_upon_recommendation:buy: ' + str(e))
            elif action == 'sell':
                try:
                    response = {} if not settings.MAKE_TRADES else poo.sell(t.symbol, rate, t.amount)
                except Exception as e:
                    print_and_log('(st)act_upon_recommendation:sell: ' + str(e))

            t.response = response
            t.orderNumber = response.get('orderNumber', '')
            t.status = 'error' if response.get('error', False) else 'open'
            t.calculatefees()
            t.calculate_exchange_rates()
            t.save()

            ot = t.opposite_trade
            ot.opposite_price = rate
            ot.net_profit = ((rate * t.amount) - (ot.price * ot.amount) if action == 'sell' else
                             (ot.price * ot.amount) - (rate * t.amount)) - ot.fee_amount - t.fee_amount
            ot.calculate_profitability_exchange_rates()
            ot.save()
