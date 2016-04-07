from django.core.management.base import BaseCommand
from django.conf import settings
from history.tools import get_fee_amount
from history.models import Price, TradeRecommendation, PerformanceComp
import datetime


class Command(BaseCommand):

    help = 'compares market perf vs nn_perf'

    def handle(self, *args, **options):
        # setup
        buffer_between_prediction_and_this_script_mins = datetime.datetime.now().minute % 10
        granularity_mins = settings.TRADER_GRANULARITY_MINS
        ticker = 'BTC_ETH'

        # get data
        date_of_timerange_we_care_about_predictions_start = datetime.datetime.now() - datetime.timedelta(
            seconds=((granularity_mins) * 60 + (60 * (1 + buffer_between_prediction_and_this_script_mins))))
        date_of_timerange_we_care_about_predictions_end = datetime.datetime.now() - datetime.timedelta(
            seconds=((granularity_mins) * 60))
        tr_timerange_end = TradeRecommendation.objects.filter(
            symbol=ticker, created_on__gte=date_of_timerange_we_care_about_predictions_start,
            created_on__lte=date_of_timerange_we_care_about_predictions_end).order_by('-created_on').first().created_on
        tr_timerange_start = tr_timerange_end - datetime.timedelta(seconds=120)
        price_timerange_start = tr_timerange_end
        price_timerange_end = tr_timerange_end + datetime.timedelta(seconds=(granularity_mins * 60))
        trs = TradeRecommendation.objects.filter(created_on__gte=tr_timerange_start, created_on__lte=tr_timerange_end)
        price_now = Price.objects.filter(symbol=ticker, created_on__lte=price_timerange_end
                                         ).order_by('-created_on').first().price
        price_then = Price.objects.filter(symbol=ticker, created_on__lte=price_timerange_start
                                          ).order_by('-created_on').first().price

        # nn attributes
        pct_buy = round(1.0 * sum(tr.recommendation == 'BUY' for tr in trs) / len(trs), 2)
        pct_sell = round(1.0 * sum(tr.recommendation == 'SELL' for tr in trs) / len(trs), 2)
        pct_hold = round(1.0 * sum(tr.recommendation == 'HOLD' for tr in trs) / len(trs), 2)
        price_diff = price_now - price_then
        price_pct = price_diff / price_then
        # -1 = sell, 0 = hold, 1 = wait
        price_buy_hold_sell = 0 if abs(price_pct) < get_fee_amount() else (1 if price_pct > 0 else -1)
        avg_nn_rec = 1.0 * sum(tr.net_amount for tr in trs) / len(trs)
        weighted_avg_nn_rec = 1.0 * sum(tr.net_amount * (tr.confidence / 100.0) for tr in trs) / len(trs)
        directionally_same = ((avg_nn_rec > 0 and price_buy_hold_sell > 0) or
                              (avg_nn_rec < 0 and price_buy_hold_sell < 0))
        delta = abs(abs(avg_nn_rec) - abs(price_buy_hold_sell)) * (1 if directionally_same else -1)

        pc = PerformanceComp(symbol=ticker,
                             price_timerange_start=price_timerange_start,
                             price_timerange_end=price_timerange_end,
                             tr_timerange_start=tr_timerange_start,
                             tr_timerange_end=tr_timerange_end,
                             nn_rec=avg_nn_rec,
                             actual_movement=price_buy_hold_sell,
                             delta=delta,
                             pct_buy=pct_buy,
                             pct_sell=pct_sell,
                             pct_hold=pct_hold,
                             rec_count=trs.count(),
                             weighted_avg_nn_rec=weighted_avg_nn_rec,
                             directionally_same=directionally_same,
                             directionally_same_int=1 if directionally_same else 0,
                             created_on_str=(tr_timerange_end - datetime.timedelta(hours=7)).strftime('%Y-%m-%d %H:%M'))
        pc.save()
