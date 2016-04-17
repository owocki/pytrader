from django.core.management.base import BaseCommand
from history.models import Price, PredictionTest, Trade, TradeRecommendation, Balance, get_time, ClassifierTest
from history.tools import get_utc_unixtime, print_and_log
import datetime
import time
from history.poloniex import poloniex
from django.conf import settings
from django.utils import timezone

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)


class Command(BaseCommand):

    help = 'mocks trading'

    def setup(self):
        # setup
        self.predictor_configs = settings.TRADER_CURRENCY_CONFIG

    def handle_open_orders(self):

        tickers = list(set([o['symbol'] for o in self.predictor_configs]))

        for ticker in tickers:
            try:
                # cancel any filled open orders
                open_orders = [] if not settings.MAKE_TRADES else self.poo.returnOpenOrders(ticker)
                for order in open_orders:
                    orderNumber = order['orderNumber']
                    rate = order['rate']
                    self.poo.cancel(ticker, orderNumber)
                    print_and_log('(t) -- handle_open_orders -- canceled stale order {} at rate {}'.
                                  format(orderNumber, rate))
                    for t in Trade.objects.filter(symbol=ticker, orderNumber=orderNumber):
                        t.status = 'canceled'
                        t.save()

                # update trade history
                trade_history = [] if not settings.MAKE_TRADES else self.poo.returnTradeHistory(ticker)
                orderNumbers = [th['orderNumber'] for th in trade_history]
                for t in Trade.objects.filter(symbol=ticker, orderNumber__in=orderNumbers):
                    t.status = 'fill'
                    t.save()
            except Exception as e:
                print_and_log('(t)handle_open_orders: ' + str(e))

    def decide_trade_amount(self, recommendation, i):
        config = self.predictor_configs[i]
        # TODO: set an amount in USD, then figure out base_amount in currency based upon that, not a hardcoded value.
        symbol = config['symbol']
        if symbol == 'USDT_BTC':
            amount = 0.01
        else:
            amount = 1
        amount = config['weight'] * amount
        confidence_median = 52.0
        confidence_leverage = 90.0

        # meter up & down our bet depending upon confidence
        this_confidence = self.confidence[i]
        rec = recommendation
        rec = rec.lower()
        confidence = this_confidence
        confidence_diff = confidence - confidence_median
        confidence_diff_positive = confidence_diff > 0
        # hey, look! an XOR
        if rec != 'hold':
            multiplier = 1 + (abs(confidence_diff) / confidence_leverage)
            if confidence_diff_positive:
                amount = amount * multiplier
            elif not confidence_diff_positive:
                amount = amount / multiplier

            # debugging info
            """
            print_and_log('(t)---- decide trade amount --- amount: {}, multiplier: {}, confidence_diff: {},\
                            confidence: {} confidence_diff_positive: {} '.\
                          format(round(amount,2),round(multiplier,2),round(confidence_diff, 2),
                                 int(confidence),confidence_diff_positive))
            """

        return amount

    def get_portfolio_breakdown(self):
        bs = Balance.objects.filter(created_on__gt=(timezone.now() - datetime.timedelta(minutes=int(5))))
        if len(bs) == 0:
            bs = Balance.objects.filter(created_on__gt=(timezone.now() - datetime.timedelta(minutes=int(10))))
        return [(b.symbol, b.btc_balance) for b in bs]

    def get_portfolio_breakdown_pct(self):
        balances_btc = self.get_portfolio_breakdown()
        portfolio_value = sum([b[1] for b in balances_btc])
        return [(b[0], round(100.0 * b[1] / portfolio_value, 1)) for b in balances_btc]

    def act_upon_recommendation(self, i, recommendation):
        # setup
        config = self.predictor_configs[i]
        currencyPair = config['symbol']

        # bid right below the lowest ask, or right above the highest bid so that our orders get filled
        price = Price.objects.filter(symbol=currencyPair).order_by('-created_on').first()
        if recommendation == 'sell':
            rate = price.lowestask * 0.999
        else:
            rate = price.highestbid * 1.001

        # decide action
        action = recommendation.lower()
        amount = 0.00
        if action in ['buy', 'sell']:
            amount = self.decide_trade_amount(action, i)

        # do items
        response = {}
        if action == 'buy':
            try:
                response = {} if not settings.MAKE_TRADES else self.poo.buy(currencyPair, rate, amount)
            except Exception as e:
                print_and_log('(t)act_upon_recommendation:buy: ' + str(e))
        elif action == 'sell':
            try:
                response = {} if not settings.MAKE_TRADES else self.poo.sell(currencyPair, rate, amount)
            except Exception as e:
                print_and_log('(t)act_upon_recommendation:sell: ' + str(e))
        else:
            print_and_log('(t)---- act_upon_recommendation declining to act.  NNs not decisive')

        if response or not settings.MAKE_TRADES:
            print_and_log('(t)---- act_upon_recommendation performing {} for {} units. response from api: {}'.
                          format(action, amount, response))

            # make this trade now
            t = Trade(type=action,
                      symbol=currencyPair,
                      price=rate,
                      amount=amount,
                      response=response,
                      orderNumber=response.get('orderNumber', ''),
                      status='error' if response.get('error', False) else 'open',
                      net_amount=((1 if action == 'buy' else -1) * amount))
            t.calculatefees()
            t.calculate_exchange_rates()
            t.save()
            self.trs[i].trade = t
            self.trs[i].save()

            if not response.get('error', False):

                # make opposite trade in {granularity} minutes
                ot = Trade(type='buy' if action == 'sell' else 'sell',
                           symbol=currencyPair,
                           price=0,
                           amount=amount,
                           response='',
                           orderNumber='',
                           status='scheduled',
                           net_amount=((1 if action == 'sell' else -1) * amount),
                           created_on=(datetime.datetime.now() + datetime.timedelta(minutes=config['granularity'])))
                ot.save()

                # make this trade now
                t.opposite_trade = ot
                ot.opposite_trade = t
                t.save()
                ot.save()

    def run_predictor(self, nn_index):
        predictor = self.predictors[nn_index]
        config = self.predictor_configs[nn_index]
        normalize = config['type'] == 'nn'
        prices = predictor.get_latest_prices(normalize=normalize)
        prices = prices[(len(prices) - predictor.datasetinputs):(len(prices) + 1)]
        recommend, nn_price, last_sample, projected_change_pct = predictor.predict(prices)
        confidence = predictor.confidence()
        if config['type'] == 'nn':
            clf = None
            made_by = predictor
        else:
            clf = predictor
            made_by = None

        print_and_log("(t)({})---- ({} w. {}% conf) ---- price from {} => {}({}% change); ".
                      format(nn_index, recommend, round(confidence, 0), round(last_sample, 4),
                             round(nn_price, 4), int(projected_change_pct * 100.0)))
        tr = TradeRecommendation(symbol=config['symbol'],
                                 made_on=str(prices),
                                 made_by=made_by,
                                 clf=clf,
                                 confidence=confidence,
                                 recommendation=recommend,
                                 net_amount=-1 if recommend == 'SELL' else (1 if recommend == 'BUY' else 0),
                                 created_on_str=str(get_time().strftime('%Y-%m-%d %H:%M')))
        tr.save()
        self.trs[nn_index] = tr
        return recommend

    def get_traders(self):
        predictors = {}
        self.confidence = {}
        self.trs = {}
        self.predictor_configs.reverse()
        for i in range(0, len(self.predictor_configs)):
            config = self.predictor_configs[i]
            if config['type'] == 'nn':
                pt = PredictionTest()
                pt.type = 'real'
                pt.symbol = config['symbol']
                pt.datasetinputs = config['datasetinputs']
                pt.hiddenneurons = 5
                pt.minutes_back = 100
                pt.epochs = 1000
                pt.momentum = 0.1
                pt.granularity = config['granularity']
                pt.bias = True
                pt.learningrate = 0.05
                pt.weightdecay = 0.0
                pt.recurrent = True
                pt.timedelta_back_in_granularity_increments = 0
                pt.save()
                predict_runtime = pt.predict_runtime()
                predict_confidence = pt.confidence()
                print_and_log("(t)predicted trainingtime for nn #{} {}: {}s, predicted confidence: {}%".
                              format(i, config['name'], round(predict_runtime, 1), int(predict_confidence)))
                pt.get_nn(train=settings.MAKE_TRADES)
                print_and_log("(t)done training")
                predictors[i] = pt
                self.confidence[i] = predict_confidence
            else:
                ct = ClassifierTest(name=config['name'],
                                    type='real',
                                    symbol=config['symbol'],
                                    datasetinputs=config['datasetinputs'],
                                    granularity=config['granularity'],
                                    minutes_back=config['minutes_back'],
                                    timedelta_back_in_granularity_increments=0)
                predict_runtime = ct.predict_runtime()
                predict_confidence = ct.confidence()
                print_and_log("(t)predicted trainingtime for nn #{} {}: {}s, predicted confidence: {}%".
                              format(i, config['name'], round(predict_runtime, 1), int(predict_confidence)))
                ct.get_classifier(test=False)
                print_and_log("(t)done training")
                predictors[i] = ct
                self.confidence[i] = predict_confidence
                ct.save()

        self.predictors = predictors
        return self.predictors

    def handle(self, *args, **options):
        # setup
        self.poo = poloniex(settings.API_KEY, settings.API_SECRET)
        self.setup()
        print_and_log("(t){} ---- ****** STARTING TRAINERS  ******* ".format(str(datetime.datetime.now())))
        self.get_traders()
        print_and_log("(t){} ---- ****** DONE TRAINING ALL TRAINERS  ******* ".format(str(datetime.datetime.now())))

        while True:

            # TLDR -- which NNs should run at this granularity?
            should_run = []
            recommendations = dict.fromkeys(range(0, len(self.predictors)))

            for i in range(0, len(self.predictor_configs)):
                config = self.predictor_configs[i]
                if (int(get_utc_unixtime() / 60) % config['granularity'] == 0 and datetime.datetime.now().second < 1):
                    should_run.append(i)

            # TLDR -- update open orders bfore placing new ones
            if len(should_run) > 0:
                self.handle_open_orders()

            # TLDR -- run the NNs specified at this granularity
            for i in should_run:
                config = self.predictor_configs[i]
                recommend = self.run_predictor(i)
                recommendations[i] = recommend
                time.sleep(1)

            # TLDR - act upon recommendations
            for i in range(0, len(recommendations)):
                recommendation = recommendations[i]
                config = self.predictor_configs[i]
                if recommendation is not None:
                    print_and_log("(t)recommendation {} - {} : {}".format(i, str(config['name']), recommendation))
                    self.act_upon_recommendation(i, recommendation)

            # TLDR - cleanup and stats
            if len(should_run) > 0:
                pct_buy = round(100.0 * sum(recommendations[i] == 'BUY' for
                                            i in recommendations) / len(recommendations))
                pct_sell = round(100.0 * sum(recommendations[i] == 'SELL' for
                                             i in recommendations) / len(recommendations))
                print_and_log("(t)TLDR - {}% buy & {}% sell: {}".format(pct_buy, pct_sell, recommendations))
                print_and_log("(t) ******************************************************************************* ")
                print_and_log("(t) portfolio is {}".format(self.get_portfolio_breakdown_pct()))
                print_and_log("(t) ******************************************************************************* ")
                print_and_log("(t) {} ..... waiting again ..... ".format(str(datetime.datetime.now())))
                print_and_log("(t) ******************************************************************************* ")

            time.sleep(1)
