import time
import datetime
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def print_and_log(log_string):
    with open(settings.LOG_FILE, "a") as myfile:
        myfile.write(log_string + "\n")
    print(log_string)


def get_utc_unixtime():
    import time
    import datetime

    d = datetime.datetime.now()
    unixtime = time.mktime(d.timetuple())
    return int(unixtime)


def create_sample_row(data, i, size):
    sample = ()
    for k in range(0, size):
        sample = sample + (data[i + k],)
    return sample


def normalization(data, new_max=1, new_min=0):
    old_max = 0
    old_min = 0

    # Finde altes Max- und Minimum
    for i in range(len(data)):
        if old_max < data[i]:
            old_max = data[i]
        elif old_min > data[i]:
            old_min = data[i]

    old_range = (old_max - old_min)

    for i in range(len(data)):
        if old_range == 0:
            data[i] = new_min
        else:
            new_range = (new_max - new_min)
            data[i] = (((data[i] - old_min) * new_range) / old_range) + new_min
    return data


def filter_by_mins(data, mins=5):
    new_data = []

    for ele in data:
        ele_unixtime = int(time.mktime(ele.created_on.timetuple()))
        ele_unixtime_min = int(ele_unixtime / 60)
        if ele_unixtime_min % mins == 0:
            new_data.append(ele)

    return new_data


def median_value(queryset, term):
    count = queryset.count()
    return queryset.values_list(term, flat=True).order_by(term)[int(round(count / 2))]


def get_exchange_rate_to_btc(ticker, d=None):
    from history.models import Price

    if d is None:
        d = datetime.datetime.now()
    if ticker == 'BTC':
        return 1

    try:
        exchange_pair = 'BTC_' + ticker
        latest_price = Price.objects.filter(symbol=exchange_pair, created_on__lt=d).order_by('-created_on').first()
        return latest_price.price
    except:
        exchange_pair = ticker + '_BTC'
        latest_price = Price.objects.filter(symbol=exchange_pair, created_on__lt=d).order_by('-created_on').first()
        return 1.0 / latest_price.price


def get_exchange_rate_btc_to_usd(d=None):
    from history.models import Price
    if d is None:
        d = datetime.datetime.now()

    exchange_pair = 'USDT_BTC'
    latest_price = Price.objects.filter(symbol=exchange_pair, created_on__lt=d).order_by('-created_on').first()
    return latest_price.price


def get_cost_basis(total_amount, symbol):
    from history.models import Trade
    running_amount = total_amount
    cost_basis_array = []
    ts = Trade.objects.filter(symbol=symbol).order_by('-created_on').values_list('amount', 'price')
    for t in ts:
        if running_amount < 0:
            continue
        trade_amount = t[0]
        price = t[1]
        if running_amount < trade_amount:
            cost_basis_array.append([running_amount, price])
        else:
            cost_basis_array.append([trade_amount, price])
        running_amount = running_amount - trade_amount

    total_amount = sum([t[0] for t in cost_basis_array])
    total_paid = sum([t[0] * t[1] for t in cost_basis_array])

    return total_paid / total_amount


def get_deposit_balance():
    from history.models import Deposit
    btc_deposit_amount = 0
    usd_deposit_amount = 0
    for d in Deposit.objects.all():
        exchange_rate = get_exchange_rate_to_btc(d.symbol, d.created_on)
        btc_amount = d.amount * exchange_rate
        usd_amount = get_exchange_rate_btc_to_usd(d.created_on) * btc_amount
        btc_deposit_amount = btc_deposit_amount + btc_amount
        usd_deposit_amount = usd_deposit_amount + usd_amount
    return btc_deposit_amount, usd_deposit_amount


def get_fee_amount(volume=settings.TRADE_VOLUME_TRAILING_30_DAYS, mode=settings.TRADE_MODE):
    for meta in settings.FEES['poloniex']:
        if meta['volume'] == volume:
            return meta[mode]

    raise ImproperlyConfigured('could not find fee amount for {} / {}'.format(volume, mode))
