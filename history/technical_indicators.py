# from https://github.com/matplotlib/matplotlib/blob/master/examples/pylab_examples/finance_work2.py
# SEE ALSO LISCENSE_MATPLOTLIB

import numpy as np
import pandas as pd


def moving_average(x, n, type='simple'):
    """
    compute an n period moving average.

    type is 'simple' | 'exponential'

    """
    x = np.asarray(x)
    if type == 'simple':
        weights = np.ones(n)
    else:
        weights = np.exp(np.linspace(-1., 0., n))

    weights /= weights.sum()

    a = np.convolve(x, weights, mode='full')[:len(x)]
    a[:n] = a[n]
    return a


def relative_strength(prices, n=14):
    """
    compute the n period relative strength indicator
    http://stockcharts.com/school/doku.php?id=chart_school:glossary_r#relativestrengthindex
    http://www.investopedia.com/terms/r/rsi.asp
    """

    deltas = np.diff(prices)
    seed = deltas[:n + 1]
    up = seed[seed >= 0].sum() / n
    down = -seed[seed < 0].sum() / n
    rs = up / down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100. / (1. + rs)

    for i in range(n, len(prices)):
        delta = deltas[i - 1]  # cause the diff is 1 shorter

        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up * (n - 1) + upval) / n
        down = (down * (n - 1) + downval) / n

        rs = up / down
        rsi[i] = 100. - 100. / (1. + rs)

    return rsi


def moving_average_convergence(x, nslow=26, nfast=12):
    """
    compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
    return value is emaslow, emafast, macd which are len(x) arrays
    """
    emaslow = moving_average(x, nslow, type='exponential')
    emafast = moving_average(x, nfast, type='exponential')
    return emaslow, emafast, emafast - emaslow


# thanks http://stackoverflow.com/questions/28477222/python-pandas-calculate-ichimoku-chart-components
def ichimoku(price_objs):
    """
    computes the ichimoku cloud for price_objs
    """

    dates = [pd.to_datetime(str(obj.created_on)) for obj in price_objs]
    prices = [obj.price for obj in price_objs]

    d = {'date': dates,
         'price': prices}
    _prices = pd.DataFrame(d)

    # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
    period9_high = pd.rolling_max(_prices['price'], window=9)
    period9_low = pd.rolling_min(_prices['price'], window=9)
    tenkan_sen = (period9_high + period9_low) / 2

    # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
    period26_high = pd.rolling_max(_prices['price'], window=26)
    period26_low = pd.rolling_min(_prices['price'], window=26)
    kijun_sen = (period26_high + period26_low) / 2

    # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)

    # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
    period52_high = pd.rolling_max(_prices['price'], window=52)
    period52_low = pd.rolling_min(_prices['price'], window=52)
    senkou_span_b = ((period52_high + period52_low) / 2).shift(26)

    # The most current closing price plotted 22 time periods behind (optional)
    chikou_span = _prices.shift(-22)  # 22 according to investopedia

    return {
        'tenkan_sen': tenkan_sen,
        'kijun_sen': kijun_sen,
        'senkou_span_a': senkou_span_a,
        'senkou_span_b': senkou_span_b,
        'chikou_span': chikou_span,
    }
