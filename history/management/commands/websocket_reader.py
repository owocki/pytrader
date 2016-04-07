try:
    import asyncio
except ImportError:
    import trollius as asyncio
from autobahn.asyncio.wamp import ApplicationRunner, ApplicationSession
from django.core.management.base import BaseCommand
from history.models import Price
import time


class MainReader(ApplicationSession):
    """
    Class that deals with the primary import of data from upstream, in this case, it happens to be poloinex
    """

    @asyncio.coroutine
    def onJoin(self, details):

        def poloniex_ticker_event(*args):
            """
            Function for handling inbound ticket events specifically from Poloniex
            Poloniex API Format is all ARG based:
            (u'BTC_NAUT', u'0.00006187', u'0.00006349', u'0.00006194', u'-0.10888664', u'2.97072995', u'50054.25243729',
            0, u'0.00007271', u'0.00005300')
            Spammy right?
            Format by line:
            0 - Currency Pair
            1 - Last Trade
            2 - Lowest Ask
            3 - Highest Bid
            4 - Percent Change
            5 - Base Volume
            6 - Quote Volume
            7 - Is Frozen
            8 - 24 Hour High
            9 - 24 Hour low
            """
            this_price = args[1]
            this_volume = args[6]
            the_str = args[0] + ',' + str(time.time()) + ',' + this_price + ", " + this_volume
            print("(pp)" + the_str)
            p = Price()
            p.price = this_price
            p.volume = this_volume
            p.lowestask = args[2]
            p.highestbid = args[3]
            p.symbol = args[0]
            p.created_on_str = str(p.created_on)
            p.save()
            print("Got ticker event for {}".format(args[0]))

        for v in self.subscribe(poloniex_ticker_event, u'ticker'):
            yield v


class Command(BaseCommand):
    help = 'Websocket handler for taking data from a remote WSAPI and inserting into the DB.'
    runner = ApplicationRunner(u"wss://api.poloniex.com", u'realm1')
    runner.run(MainReader)

if __name__ == '__main__':
    runner = ApplicationRunner(u"wss://api.poloniex.com", u'realm1')
    runner.run(MainReader)
