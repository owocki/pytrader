from django.contrib.admin.views.decorators import staff_member_required
from history.models import (
    PredictionTest, Price, Trade, Balance, TradeRecommendation, get_time, PerformanceComp,
    ClassifierTest)
from django.shortcuts import render_to_response
from django.utils import timezone
import datetime
from django.db.models import Avg, Max, Min, Sum, Count
# Create your views here.
from chartit import DataPool, Chart, PivotDataPool, PivotChart
from history.tools import median_value, get_cost_basis
from django.conf import settings


def getify(dic):
    st = str()
    for K, V in dic.iteritems():
        if type(V) is list:
            for v in V:
                st += K+'='+v+'&'
        else:
            st += K+'='+V+'&'
    return st.rstrip('&')


def get_scatter_chart(pts, x_axis, symbol):
        data = DataPool(series=[{'options': {'source': pts}, 'terms': [x_axis, 'percent_correct']}])

        # Step 2: Create the Chart object
        cht = Chart(
            datasource=data,
            series_options=[
                {'options': {
                    'type': 'scatter'},
                    'terms': {
                        x_axis: [
                            'percent_correct']
                    }}],
            chart_options={
                'title': {
                    'text': '{} percent correct by {}'.format(symbol, x_axis)},
                'xAxis': {
                    'title': {
                        'text': x_axis}}})
        return cht


def get_line_chart(pts, symbol, parameter):
    # sorting hack
    for pt in pts:
        if pt.percent_correct == 100.0:
            pt.percent_correct = 99.9

    ds = PivotDataPool(
        series=[
            {'options': {
                'source': pts.order_by('-'+parameter).all(),
                'categories': parameter},
                'terms': {
                    'tot_items': Count(parameter)}}])

    pivcht = PivotChart(
        datasource=ds,
        series_options=[
            {'options': {
                'type': 'column'},
                'terms': ['tot_items']}],
        chart_options={
            'title': {
                'text': 'Distribution of '+parameter+' %s'},
            'xAxis': {
                'title': {
                    'text': 'Percent'}}}
    )
    return pivcht


def get_data(request, symbol, table_name='history_predictiontest', table=PredictionTest):
    query = "select * from {} WHERE type = 'mock' and symbol = '{}'".format(table_name, symbol)
    i = 0
    for key, value in request.GET.items():
        if key not in ['days_ago', 'hours_ago']:
            i += 1
            query = query + " and {} = '{}' ".format(key, value)
    try:
        pts = table.objects.raw(query)
        pt_pks = [pt.pk for pt in pts]
    except Exception:
        i = 0
        pass
    has_filtered = i > 0
    if has_filtered:
        pts = table.objects.filter(type='mock', symbol=symbol, pk__in=pt_pks).all()
    else:
        pts = table.objects.filter(type='mock', symbol=symbol).all()
    days_ago = request.GET.get('days_ago', False)
    hours_ago = request.GET.get('hours_ago', False)
    if not hours_ago and not days_ago:
        hours_ago = 6
    if days_ago:
        pts = pts.filter(created_on__gte=(timezone.now() - datetime.timedelta(days=int(days_ago))))
    if hours_ago:
        pts = pts.filter(created_on__gte=(timezone.now() - datetime.timedelta(hours=int(hours_ago))))

    symbols_that_exist = table.objects.values_list('symbol', flat=True).distinct()

    return pts, symbols_that_exist


def get_balance_breakdown_chart(bs, denom, symbol, start_time):

    ds = PivotDataPool(
        series=[
            {'options': {
                'source': bs.filter(created_on__gte=start_time).order_by('-created_on').all(),
                'categories': 'date_str',
                'legend_by': 'symbol'},
                'terms': {
                    'total_value': Sum(denom)}}])

    pivcht = PivotChart(
        datasource=ds,
        series_options=[
            {'options': {
                'type': 'column',
                'stacking': True,
                'xAxis': 0,
                'yAxis': 0},
                'terms': ['total_value']}],
        chart_options={
            'title': {
                'text': 'Balance over time ('+denom+') '},
            'xAxis': {
                'title': {
                    'text': 'Time'}},
            'terms': ['total_value']
        }
    )
    return pivcht


def get_balance_chart(bs, denom, symbol, start_time):

    dep_amount_fieldname = 'deposited_amount_usd' if denom != 'btc_balance' else 'deposited_amount_btc'

    ds = PivotDataPool(
        series=[
            {'options': {
                'source': bs.filter(created_on__gte=start_time).order_by('-created_on').all(),
                'categories': 'date_str'
            },
                'terms': {
                    'total_value': Sum(denom), 'total_invested': Sum(dep_amount_fieldname),
                }}])

    pivcht = PivotChart(
        datasource=ds,
        series_options=[
            {'options': {
                'type': 'line',
                'xAxis': 0,
                'yAxis': 0},
                'terms': ['total_value', 'total_invested']}],
        chart_options={
            'title': {
                'text': 'Balance over time ('+denom+') '},
            'xAxis': {
                'title': {
                    'text': 'Time'}},
            'terms': ['total_value', 'total_invested']
        }
    )
    return pivcht


def get_trade_chart(bs, denom, symbol, start_time):

    if settings.MAKE_TRADES:
        trades = Trade.objects.exclude(created_on_str="").filter(
            symbol=symbol, created_on__gte=start_time).filter(status__in=['fill', 'open', 'error']).order_by('id')
    else:
        trades = Trade.objects.exclude(created_on_str="").filter(
            symbol=symbol, created_on__gte=start_time).order_by('id')

    ds = PivotDataPool(
        series=[
            {'options': {
                'source': trades,
                'categories': 'created_on_str',
                'legend_by': 'status'},
                'terms': {
                    'total_value': Sum('net_amount')}}])

    pivcht = PivotChart(
        datasource=ds,
        series_options=[
            {'options': {
                'type': 'column',
                'stacking': True,
                'xAxis': 0,
                'yAxis': 0},
                'terms': ['total_value']}],
        chart_options={
            'title': {
                'text': 'Trades over time '},
            'xAxis': {
                'title': {
                    'text': 'Time'}},
            'terms': ['total_value']
        }
    )

    return pivcht


def get_trade_profitability_chart(bs, denom, symbol, start_time):

    if settings.MAKE_TRADES:
        trades = Trade.objects.exclude(created_on_str="").filter(
            symbol=symbol, created_on__gte=start_time).filter(status__in=['fill', 'open', 'error']).order_by('id')
    else:
        trades = Trade.objects.exclude(created_on_str="").filter(
            symbol=symbol, created_on__gte=start_time).order_by('id')

    ds = PivotDataPool(
        series=[
            {'options': {
                'source': trades,
                'categories': 'created_on_str',
                'legend_by': 'status'},
                'terms': {
                    'total_value': Sum('btc_net_profit')}}])

    pivcht = PivotChart(
        datasource=ds,
        series_options=[
            {'options': {
                'type': 'column',
                'stacking': True,
                'xAxis': 0,
                'yAxis': 0},
                'terms': ['total_value']}],
        chart_options={
            'title': {
                'text': 'Trade Profitability over time (BTC) '},
            'xAxis': {
                'title': {
                    'text': 'Time'}},
            'terms': ['total_value']
        }
    )

    return pivcht


def get_performance_comps_chart(bs, denom, symbol, start_time):

    if settings.MAKE_TRADES:
        pcs = PerformanceComp.objects.filter(symbol=symbol, created_on__gte=start_time,
                                             price_timerange_start__isnull=False).order_by('id')
    else:
        pcs = PerformanceComp.objects.filter(symbol=symbol, created_on__gte=start_time,
                                             price_timerange_start__isnull=False).order_by('id')

    ds = DataPool(
        series=[
            {'options': {
                'source': pcs},
                'terms': ['created_on_str', 'delta', 'actual_movement', 'nn_rec',
                          'pct_buy', 'pct_sell', 'weighted_avg_nn_rec']}
        ])

    cht = Chart(
        datasource=ds,
        series_options=[
            {'options': {
                'type': 'line',
                'stacking': False},
                'terms': {
                    'created_on_str': ['delta', 'actual_movement', 'nn_rec',
                                       'pct_buy', 'pct_sell', 'weighted_avg_nn_rec']
                }}],
        chart_options={
            'title': {
                'text': 'Algorithm vs Reality: Debug'},
            'xAxis': {
                'title': {
                    'text': 'Time'}}})

    return cht


def get_directional_change_chart(bs, denom, symbol, start_time):

    if settings.MAKE_TRADES:
        pcs = PerformanceComp.objects.filter(symbol=symbol, created_on__gte=start_time,
                                             price_timerange_start__isnull=False).order_by('id')
    else:
        pcs = PerformanceComp.objects.filter(symbol=symbol, created_on__gte=start_time,
                                             price_timerange_start__isnull=False).order_by('id')
    pct_dir_same = int(100.0 * sum([pc.directionally_same_int for pc in pcs]) / pcs.count()) if pcs.count() != 0 else 0
    ds = PivotDataPool(
        series=[
            {'options': {
                'source': pcs,
                'categories': 'created_on_str'
            },
                'terms': {
                    'total_value': Sum('directionally_same_int')}}])

    pivcht = PivotChart(
        datasource=ds,
        series_options=[
            {'options': {
                'type': 'line',
                'xAxis': 0,
                'yAxis': 0},
                'terms': ['total_value']}],
        chart_options={
            'title': {
                'text': 'Algorithm vs Reality: Directionally Same '+str(pct_dir_same)+'% of time '},
            'xAxis': {
                'title': {
                    'text': 'Time'}},
            'terms': ['total_value']
        }
    )
    return pivcht


def get_ticker_price(bs, denom, symbol, start_time):

    p = Price.objects.none()
    for minute in [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]:
        p = p | Price.objects.exclude(created_on_str="").filter(symbol=symbol, created_on__gte=start_time,
                                                                created_on__minute=minute)
    p = p.order_by('created_on')

    ds = DataPool(
        series=[
            {'options': {
                'source': p},
                'terms': [
                    'created_on_str',
                    'price']}
        ])

    cht = Chart(
        datasource=ds,
        series_options=[
            {'options': {
                'type': 'line',
                'stacking': False},
                'terms': {
                    'created_on_str': [
                        'price']
                }}],
        chart_options={
            'title': {
                'text': 'Price Over Time {}'.format(symbol)},
            'xAxis': {
                'title': {
                    'text': 'Time'}}})
    return cht


@staff_member_required
def nn_chart_view(request):

    # setup
    symbol = request.GET.get('symbol', 'BTC_ETH')
    i = 0
    charts = []
    chartnames = []
    metas = []
    symbols = Price.objects.values('symbol').distinct().order_by('symbol').values_list('symbol', flat=True)

    # get data
    pts, symbols_that_exist = get_data(request, symbol)
    if len(pts) == 0:
        return render_to_response('notfound.html')

    trainer_last_seen = None
    try:
        last_pt = PredictionTest.objects.filter(type='mock').order_by('-created_on').first()
        is_trainer_running = last_pt.created_on > (get_time() - datetime.timedelta(minutes=int(15)))
        trainer_last_seen = (last_pt.created_on - datetime.timedelta(hours=int(7))).strftime('%a %H:%M')
    except Exception:
        is_trainer_running = False

    meta = {
        'count': int(round(pts.count(), 0)),
        'avg': round(pts.aggregate(Avg('percent_correct'))['percent_correct__avg'], 0),
        'median': round(median_value(pts, 'percent_correct'), 0),
        'max': round(pts.aggregate(Max('percent_correct'))['percent_correct__max'], 0),
        'min': round(pts.aggregate(Min('percent_correct'))['percent_correct__min'], 0),
    }

    # get global chart information
    for parameter in ['percent_correct', 'profitloss_int']:
        i = i + 1
        cht = get_line_chart(pts, symbol, parameter)
        charts.append(cht)
        options = []
        chartnames.append("container"+str(i))
        metas.append({
            'name': parameter,
            'container_class': 'show',
            'class': "container"+str(i),
            'options': options,
        })

    # get parameter distribution charts
    parameters = ['datasetinputs', 'hiddenneurons', 'granularity', 'minutes_back', 'epochs', 'learningrate',
                  'momentum', 'weightdecay', 'bias_chart', 'recurrent_chart',
                  'timedelta_back_in_granularity_increments', 'time', 'prediction_size']
    for x_axis in parameters:
        i = i + 1
        cht = get_scatter_chart(pts, x_axis, symbol)
        charts.append(cht)
        options_dict = pts.values(x_axis).annotate(Avg('percent_correct')).annotate(Count('pk'))
        options = [(x_axis, obj[x_axis], int(round(obj['percent_correct__avg'], 0)),
                    int(round(obj['pk__count'], 0))) for obj in options_dict]
        options.sort(key=lambda x: x[1])
        the_max = max([option[2] for option in options])
        for k in range(len(options)):
            options[k] = options[k] + (("max" if options[k][2] == the_max else "notmax") +
                                       " " + ("warning" if options[k][3] < 5 else "nowarning"),)
        chartnames.append("container"+str(i))
        metas.append({
            'name': x_axis,
            'container_class': 'show' if len(options) > 1 else 'noshow',
            'class': "container"+str(i),
            'options': options,
        })

    # Step 3: Send the chart object to the template.
    return render_to_response('chart.html', {
        'pts': pts.order_by('percent_correct'),
        'ticker': symbol,
        'symbols': symbols,
        'meta': meta,
        'days_ago': [1, 2, 3, 4, 5, 10, 15, 30],
        'hours_ago': [1, 2, 3, 6, 12, 24],
        'getparams': getify(request.GET),
        'charts': charts,
        'metas': metas,
        'chartnames': chartnames,
        'chartnamesstr': ",".join(chartnames),
        'is_trainer_running': is_trainer_running,
        'trainer_last_seen': trainer_last_seen,
        'symbols_that_exist': symbols_that_exist,
    })


@staff_member_required
def c_chart_view(request):

    # setup
    symbol = request.GET.get('symbol', 'BTC_ETH')
    i = 0
    charts = []
    chartnames = []
    metas = []
    symbols = Price.objects.values('symbol').distinct().order_by('symbol').values_list('symbol', flat=True)

    # get data
    pts, symbols_that_exist = get_data(request, symbol, 'history_classifiertest', ClassifierTest)

    if len(pts) == 0:
        return render_to_response('notfound.html')

    trainer_last_seen = None
    try:
        last_pt = ClassifierTest.objects.filter(type='mock').order_by('-created_on').first()
        is_trainer_running = last_pt.created_on > (get_time() - datetime.timedelta(minutes=int(15)))
        trainer_last_seen = (last_pt.created_on - datetime.timedelta(hours=int(7))).strftime('%a %H:%M')
    except Exception:
        is_trainer_running = False

    meta = {
        'count': int(round(pts.count(), 0)),
        'avg': round(pts.aggregate(Avg('percent_correct'))['percent_correct__avg'], 0),
        'median': round(median_value(pts, 'percent_correct'), 0),
        'max': round(pts.aggregate(Max('percent_correct'))['percent_correct__max'], 0),
        'min': round(pts.aggregate(Min('percent_correct'))['percent_correct__min'], 0),
    }

    # get global chart information
    for parameter in ['percent_correct', 'score']:
        i = i + 1
        cht = get_line_chart(pts, symbol, parameter)
        charts.append(cht)
        options = []
        chartnames.append("container"+str(i))
        metas.append({
            'name': parameter,
            'container_class': 'show',
            'class': "container"+str(i),
            'options': options,
        })

    # get parameter distribution charts
    parameters = ['name', 'datasetinputs', 'granularity', 'minutes_back',
                  'timedelta_back_in_granularity_increments', 'time', 'prediction_size']
    for x_axis in parameters:
        i = i + 1
        cht = get_scatter_chart(pts, x_axis, symbol)
        charts.append(cht)
        options_dict = pts.values(x_axis).annotate(Avg('percent_correct')).annotate(Count('pk'))
        options = [(x_axis, obj[x_axis], int(round(obj['percent_correct__avg'], 0)),
                    int(round(obj['pk__count'], 0))) for obj in options_dict]
        options.sort(key=lambda x: x[1])
        the_max = max([option[2] for option in options])
        for k in range(len(options)):
            options[k] = options[k] + (("max" if options[k][2] == the_max else "notmax") +
                                       " " + ("warning" if options[k][3] < 5 else "nowarning"),)
        chartnames.append("container"+str(i))
        metas.append({
            'name': x_axis,
            'container_class': 'show' if len(options) > 1 else 'noshow',
            'class': "container"+str(i),
            'options': options,
        })

    # Step 3: Send the chart object to the template.
    return render_to_response('c_chart.html', {
        'pts': pts.order_by('percent_correct'),
        'ticker': symbol,
        'symbols': symbols,
        'meta': meta,
        'days_ago': [1, 2, 3, 4, 5, 10, 15, 30],
        'hours_ago': [1, 2, 3, 6, 12, 24],
        'getparams': getify(request.GET),
        'charts': charts,
        'metas': metas,
        'chartnames': chartnames,
        'chartnamesstr': ",".join(chartnames),
        'is_trainer_running': is_trainer_running,
        'trainer_last_seen': trainer_last_seen,
        'symbols_that_exist': symbols_that_exist,
    })


@staff_member_required
def profit_view(request):

    # setup
    the_denom = request.GET.get('denom', 'btc_balance')
    denoms = ['usd_balance', 'btc_balance']
    days_ago = request.GET.get('days_ago', False)
    hours_ago = request.GET.get('hours_ago', False)
    if not hours_ago and not days_ago:
        hours_ago = 6
    if days_ago:
        start_time = (timezone.now() - datetime.timedelta(days=int(days_ago)))
    elif hours_ago:
        start_time = (timezone.now() - datetime.timedelta(hours=int(hours_ago)))
    else:
        start_time = Balance.objects.order_by('created_on').first().created_on
    symbol = 'BTC_ETH'
    this_symbol = symbol.split("_")

    # get data
    data = {}
    for t in Trade.objects.filter(symbol=symbol, status='fill').order_by('-created_on').all():
        date = datetime.datetime.strftime(t.created_on-datetime.timedelta(hours=7), '%Y-%m-%d')
        if date not in data.keys():
            data[date] = {'buyvol': [], 'sellvol': [], 'buy': [], 'sell': [], 'bal': 0.00}
        data[date][t.type].append(t.price)
        data[date][t.type+'vol'] = data[date][t.type+'vol'] + [t.amount]
        data[date]['bal'] = Balance.objects.filter(
            symbol=this_symbol[1], created_on__lte=(datetime.datetime.strptime(date, '%Y-%m-%d') +
                                                    datetime.timedelta(days=1))
        ).order_by('-created_on').values_list('coin_balance', flat=True).first()

    bs = Balance.objects.filter(created_on__gte=start_time).all()

    i = 0
    charts = []
    chartnames = []
    for func in [get_balance_chart, get_balance_breakdown_chart]:
        i = i + 1
        cht = func(bs, the_denom, symbol, start_time)
        charts.append(cht)
        chartnames.append(str(func).split()[1].replace('get_', '').replace('_chart', ''))

    num_runs = 0
    view_data = []
    for key in data.keys():
        num_runs = num_runs+1
        data[key]['symbol'] = this_symbol[1]
        data[key]['unrealizeddiff'] = round(data[key]['bal'] * Price.objects.filter(symbol=symbol).
                                            order_by('-created_on').values_list('price', flat=True).
                                            first() * get_cost_basis(data[key]['bal'], symbol), 4)
        data[key]['buyvol'] = round(sum(data[key]['buyvol']), 1)
        data[key]['sellvol'] = round(sum(data[key]['sellvol']), 1)
        data[key]['netvol'] = round((data[key]['buyvol']), 1) - round((data[key]['sellvol']), 1)
        data[key]['buy'] = 0 if len(data[key]['buy']) == 0 else sum(data[key]['buy']) / len(data[key]['buy'])
        data[key]['sell'] = 0 if len(data[key]['sell']) == 0 else sum(data[key]['sell']) / len(data[key]['sell'])
        data[key]['diff'] = (data[key]['sell'] - data[key]['buy']) * abs(data[key]['netvol'])
        view_data.append({
            'one_symbol': '' if 'symbol' not in data[key].keys() else data[key]['symbol'],
            'unrealizeddiff': '' if 'unrealizeddiff' not in data[key].keys() else data[key]['unrealizeddiff'],
            'date': key,
            'symbol': symbol,
            'netvol': data[key]['netvol'],
            'bal': round(data[key]['bal'], 1),
            'buyvol': data[key]['buyvol'],
            'sellvol': data[key]['sellvol'],
            'buy': round(data[key]['buy'], 4),
            'sell': round(data[key]['sell'], 4),
            'diff': round(data[key]['diff'], 4),
        })

    view_data = sorted(view_data, reverse=True, key=lambda vd: vd['date'])
    last_day_profit = view_data[0]['diff'] if len(view_data) > 0 else 0
    max_date = view_data[0]['date'] if len(view_data) > 0 else 0
    is_in_profit = last_day_profit > 0

    return render_to_response('profit.html', {'data': view_data,
                                              'days_ago': [1, 2, 3, 4, 5, 10, 15, 30],
                                              'hours_ago': [1, 2, 3, 6, 12, 24],
                                              'getparams': getify(request.GET),
                                              'charts': charts,
                                              'chartnames': chartnames,
                                              'chartnamesstr': ",".join(chartnames),
                                              'denoms': denoms,
                                              'the_denom': the_denom,
                                              'last_day_profit': last_day_profit,
                                              'is_in_profit': is_in_profit,
                                              'max_date': max_date,
                                              })


@staff_member_required
def optimize_view(request):

    # setup
    the_denom = request.GET.get('denom', 'btc_balance')
    denoms = ['usd_balance', 'btc_balance']
    days_ago = request.GET.get('days_ago', False)
    hours_ago = request.GET.get('hours_ago', False)
    if not hours_ago and not days_ago:
        hours_ago = 6
    if days_ago:
        start_time = (timezone.now() - datetime.timedelta(days=int(days_ago)))
    elif hours_ago:
        start_time = (timezone.now() - datetime.timedelta(hours=int(hours_ago)))
    else:
        start_time = Balance.objects.order_by('created_on').first().created_on
    symbol = 'BTC_ETH'

    # get data
    data = {}
    for t in Trade.objects.filter(symbol=symbol, status='fill').order_by('-created_on').all():
        date = datetime.datetime.strftime(t.created_on, '%Y-%m-%d')
        if date not in data.keys():
            data[date] = {'buyvol': [], 'sellvol': [], 'buy': [], 'sell': []}
        data[date][t.type].append(t.price)
        data[date][t.type+'vol'] = data[date][t.type+'vol'] + [t.amount]
    bs = Balance.objects.filter(created_on__gte=start_time).all()

    last_trade = TradeRecommendation.objects.order_by('-created_on').first()
    if last_trade:
        trader_last_seen = (last_trade.created_on - datetime.timedelta(hours=int(7))).strftime('%a %H:%M')
        is_trader_running = last_trade.created_on > (get_time() - datetime.timedelta(minutes=int(15)))
    else:
        trader_last_seen = None
        is_trader_running = False

    i = 0
    charts = []
    chartnames = []
    for func in [get_trade_chart, get_trade_profitability_chart, get_directional_change_chart,
                 get_performance_comps_chart, get_ticker_price]:
        i = i + 1
        cht = func(bs, the_denom, symbol, start_time)
        charts.append(cht)
        chartnames.append(str(func).split()[1].replace('get_', '').replace('_chart', ''))

    return render_to_response('optimize.html', {
        'days_ago': [1, 2, 3, 4, 5, 10, 15, 30],
        'hours_ago': [1, 2, 3, 6, 12, 24],
        'getparams': getify(request.GET),
        'charts': charts,
        'chartnames': chartnames,
        'chartnamesstr': ",".join(chartnames),
        'denoms': denoms,
        'the_denom': the_denom,
        'is_trader_running': is_trader_running,
        'trader_last_seen': trader_last_seen,
    })
