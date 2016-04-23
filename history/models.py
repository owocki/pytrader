from __future__ import unicode_literals
from django.utils import timezone
import datetime
from pybrain.datasets import SupervisedDataSet
from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from django.db import models
from history.tools import create_sample_row, get_fee_amount
from django.utils.timezone import localtime
from django.conf import settings
from django.core.urlresolvers import reverse
import cgi
import time
import numpy as np
import matplotlib
import textblob
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.cross_validation import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

matplotlib.use('Agg')
np.random.seed(0)


def get_time():
    return localtime(timezone.now())


class TimeStampedModel(models.Model):
    created_on = models.DateTimeField(null=False, default=get_time, db_index=True)
    modified_on = models.DateTimeField(null=False, default=get_time)

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self._meta.get_fields()]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save(self, *args, **kwargs):
        self.modified_on = get_time()
        return super(TimeStampedModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True

    def url_to_edit_object(self):
        url = reverse('admin:{0}_{1}_change'.format(self._meta.app_label, self._meta.model_name), args=[self.id])
        return '<a href="{0}">Edit {1}</a>'.format(url, cgi.escape(str(self)))


class AbstractedTesterClass(models.Model):
    created_on = models.DateTimeField(null=False, default=get_time)
    modified_on = models.DateTimeField(null=False, default=get_time)

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self._meta.get_fields()]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save(self, *args, **kwargs):
        self.modified_on = get_time()
        return super(AbstractedTesterClass, self).save(*args, **kwargs)

    class Meta:
        abstract = True

    def url_to_edit_object(self):
        url = reverse('admin:{0}_{1}_change'.format(self._meta.app_label, self._meta.model_name), args=[self.id])
        return '<a href="{0}">Edit {1}</a>'.format(url, cgi.escape(str(self)))

    def confidence(self):
        related = self.related_mocks()
        related.exclude(percent_correct__isnull=True)
        related = [rel.percent_correct for rel in related]
        if len(related) == 0:
            return 0
        return sum(related) / len(related)

    def predict_runtime(self):
        related = self.related_mocks()
        related.exclude(time=0.0)
        related = [rel.time for rel in related]
        if len(related) == 0:
            return 0.00
        return sum(related) / len(related)

    def get_train_and_test_data(self):
        data = self.get_latest_prices()

        if self.timedelta_back_in_granularity_increments == 0:
            return data, []

        sample_data = data[0:(-1 * self.timedelta_back_in_granularity_increments)]
        test_data = data[len(sample_data):]
        return sample_data, test_data

    def get_latest_prices(self, normalize=True):
        from history.tools import normalization, filter_by_mins
        splice_point = self.minutes_back + self.timedelta_back_in_granularity_increments

        prices = Price.objects.filter(symbol=self.symbol).order_by('-created_on')
        prices = filter_by_mins(prices, self.granularity)
        prices = [price.price for price in prices]
        prices = list(prices[0:splice_point])
        if normalize:
            prices = normalization(prices)
        prices.reverse()
        return prices


class Deposit(TimeStampedModel):
    symbol = models.CharField(max_length=30)
    amount = models.FloatField(null=True)
    type = models.CharField(max_length=10)
    txid = models.CharField(max_length=500, default='')
    status = models.CharField(max_length=100, default='none')
    created_on_str = models.CharField(max_length=50, default='')


class Trade(TimeStampedModel):
    symbol = models.CharField(max_length=30)
    price = models.FloatField()
    amount = models.FloatField(null=True)
    type = models.CharField(max_length=10)
    response = models.TextField()
    orderNumber = models.CharField(max_length=50, default='')
    status = models.CharField(max_length=10, default='none')
    net_amount = models.FloatField(null=True)
    created_on_str = models.CharField(max_length=50, default='')
    fee_amount = models.FloatField(null=True)
    btc_amount = models.FloatField(null=True)
    usd_amount = models.FloatField(null=True)
    btc_fee_amount = models.FloatField(null=True)
    usd_fee_amount = models.FloatField(null=True)
    opposite_trade = models.ForeignKey('Trade', null=True)
    opposite_price = models.FloatField(null=True)
    net_profit = models.FloatField(null=True)
    btc_net_profit = models.FloatField(null=True)
    usd_net_profit = models.FloatField(null=True)

    def calculatefees(self):
        self.fee_amount = self.amount * get_fee_amount()

    def calculate_exchange_rates(self):
        from history.tools import get_exchange_rate_to_btc, get_exchange_rate_btc_to_usd
        ticker = ''
        for this_ticker in self.symbol.split('_'):
            if this_ticker != 'BTC':
                ticker = this_ticker
        exchange_rate_coin_to_btc = get_exchange_rate_to_btc(ticker)
        exchange_rate_btc_to_usd = get_exchange_rate_btc_to_usd()
        self.btc_amount = exchange_rate_coin_to_btc * self.amount
        self.usd_amount = exchange_rate_btc_to_usd * self.btc_amount
        self.btc_fee_amount = exchange_rate_coin_to_btc * self.fee_amount
        self.usd_fee_amount = exchange_rate_btc_to_usd * self.btc_fee_amount

    def calculate_profitability_exchange_rates(self):
        from history.tools import get_exchange_rate_to_btc, get_exchange_rate_btc_to_usd
        ticker = ''
        for this_ticker in self.symbol.split('_'):
            if this_ticker != 'BTC':
                ticker = this_ticker
        exchange_rate_coin_to_btc = get_exchange_rate_to_btc(ticker)
        exchange_rate_btc_to_usd = get_exchange_rate_btc_to_usd()
        self.btc_net_profit = exchange_rate_coin_to_btc * self.net_profit
        self.usd_net_profit = exchange_rate_btc_to_usd * self.btc_net_profit

    def __str__(self):
        return 'Trade {}'.format(self.pk)


class Price(TimeStampedModel):
    symbol = models.CharField(max_length=30, db_index=True)
    price = models.FloatField()
    volume = models.FloatField(null=True)
    lowestask = models.FloatField(null=True)
    highestbid = models.FloatField(null=True)
    created_on_str = models.CharField(max_length=50, default='')


class Balance(TimeStampedModel):
    symbol = models.CharField(max_length=30)
    coin_balance = models.FloatField()
    usd_balance = models.FloatField(null=True)
    btc_balance = models.FloatField()
    exchange_to_btc_rate = models.FloatField()
    exchange_to_usd_rate = models.FloatField(null=True)
    deposited_amount_usd = models.FloatField(default=0.00)
    deposited_amount_btc = models.FloatField(default=0.00)
    date_str = models.CharField(max_length=20, default='0', db_index=True)


class PerformanceComp(TimeStampedModel):
    symbol = models.CharField(max_length=30)
    nn_rec = models.FloatField()
    actual_movement = models.FloatField()
    delta = models.FloatField()
    created_on_str = models.CharField(max_length=30)
    directionally_same = models.BooleanField(default=False)
    directionally_same_int = models.IntegerField(default=0)
    weighted_avg_nn_rec = models.FloatField(default=0)
    pct_buy = models.FloatField(default=0)
    pct_hold = models.FloatField(default=0)
    pct_sell = models.FloatField(default=0)
    rec_count = models.IntegerField(default=0)
    price_timerange_start = models.DateTimeField(null=True, default=None, db_index=True)
    price_timerange_end = models.DateTimeField(null=True, default=None, db_index=True)
    tr_timerange_start = models.DateTimeField(null=True, default=None)
    tr_timerange_end = models.DateTimeField(null=True, default=None)


class TradeRecommendation(TimeStampedModel):
    symbol = models.CharField(max_length=30)
    made_by = models.ForeignKey('PredictionTest', null=True)
    clf = models.ForeignKey('ClassifierTest', null=True)
    made_on = models.TextField(max_length=30)
    recommendation = models.CharField(max_length=30)
    confidence = models.FloatField()
    created_on_str = models.CharField(max_length=30, default='')
    net_amount = models.FloatField(default=0)
    trade = models.ForeignKey('Trade', null=True, db_index=True)


class ClassifierTest(AbstractedTesterClass):

    BUY = 1
    SELL = 0
    HOLD = -1

    type = models.CharField(max_length=30, default='mock', db_index=True)
    symbol = models.CharField(max_length=30, db_index=True)
    name = models.CharField(max_length=100, default='')
    datasetinputs = models.IntegerField()
    granularity = models.IntegerField()
    minutes_back = models.IntegerField(default=0)
    timedelta_back_in_granularity_increments = models.IntegerField(default=0)
    ###############
    time = models.IntegerField(default=0)
    prediction_size = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    output = models.TextField()
    percent_correct = models.FloatField(null=True)

    def __str__(self):
        return self.name + " on " + str(self.created_on)

    def rerun(self, keep_new_obj=False):
        pass  # todo

    def related_mocks(self):
        days_ago = 2
        return ClassifierTest.objects.filter(created_on__gt=(timezone.now() - datetime.timedelta(days=int(days_ago))),
                                             symbol=self.symbol,
                                             minutes_back=self.minutes_back,
                                             granularity=self.granularity,
                                             datasetinputs=self.datasetinputs,
                                             name=self.name,
                                             type='mock')

    def get_classifier(self, train=True, test=True):

        all_output = ""
        h = .02  # step size in the mesh
        self.names = ["Nearest Neighbors", "Linear SVM", "RBF SVM", "Decision Tree",
                      "Random Forest", "AdaBoost", "Naive Bayes", "Linear Discriminant Analysis",
                      "Quadratic Discriminant Analysis"]
        classifiers = [
            KNeighborsClassifier(3),
            SVC(kernel="linear", C=0.025),
            SVC(gamma=2, C=1),
            DecisionTreeClassifier(max_depth=5),
            RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
            AdaBoostClassifier(),
            GaussianNB(),
            LinearDiscriminantAnalysis(),
            QuadraticDiscriminantAnalysis()]

        for i in range(0, len(self.names)):
            if self.names[i] == self.name:
                clf = classifiers[i]

        if train:
            start_time = int(time.time())
            data = self.get_latest_prices(normalize=False)
            price_datasets = [[], []]
            for i, val in enumerate(data):
                try:
                    # get classifier projection
                    sample = create_sample_row(data, i, self.datasetinputs)
                    last_price = data[i + self.datasetinputs - 1]
                    next_price = data[i + self.datasetinputs]
                    change = next_price - last_price
                    pct_change = change / last_price
                    fee_pct = get_fee_amount()
                    fee_pct = fee_pct * 2  # fee x 2 since we'd need to clear both buy and sell fees to be profitable
                    fee_pct = fee_pct * settings.FEE_MANAGEMENT_STRATEGY  # see desc in settings.py
                    do_buy = ClassifierTest.HOLD if abs(pct_change) < fee_pct else (
                        ClassifierTest.BUY if change > 0 else ClassifierTest.SELL)
                    price_datasets[0].append(sample)
                    price_datasets[1].append(do_buy)
                except Exception:
                    pass

            data = price_datasets
            if self.timedelta_back_in_granularity_increments == 0:
                train_data = data
                test_data = [[], []]
            else:
                train_data = [data[0][0:(-1 * self.timedelta_back_in_granularity_increments)],
                              data[1][0:(-1 * self.timedelta_back_in_granularity_increments)]]
                test_data = [data[0][len(train_data[0]):], data[1][len(train_data[1]):]]
            self.datasets = train_data

            X, y = train_data
            X = StandardScaler().fit_transform(X)
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=.4)

            self.min = {}
            self.max = {}
            self.xz = ()
            mesh_args = []
            for i in range(0, self.datasetinputs):
                self.min[i], self.max[i] = X[:, i].min() - .5, X[:, i].max() + .5
                mesh_args.append(np.arange(self.min[i], self.max[i], h))
            self.xz = np.meshgrid(*mesh_args)

            clf.fit(self.X_train, self.y_train)
            score = clf.score(self.X_test, self.y_test)

            # Plot the decision boundary. For that, we will assign a color to each
            # point in the mesh [self.x_min, m_max]x[self.y_min, self.y_max].

            self.ravel_args = []
            for i in range(0, self.datasetinputs):
                self.ravel_args.append(self.xz[i].ravel())

            self._input = np.column_stack(self.ravel_args)

            if hasattr(clf, "decision_function"):
                self.Z = clf.decision_function(self._input)
            else:
                self.Z = clf.predict_proba(self._input)[:, 1]

            if test and len(test_data) > 0:
                stats = {'r': 0, 'w': 0, 'p': {0: 0, 1: 0, -1: 0}, 'a': {0: 0, 1: 0, -1: 0}}
                ds = test_data
                for i in range(0, len(ds[0])):
                    sample = ds[0][i]
                    actual = ds[1][i]
                    sample = StandardScaler().fit_transform(sample)
                    prediction = clf.predict(sample)
                    self.prediction = prediction
                    stats['p'][prediction[0]] += 1
                    stats['a'][actual] += 1
                    stats['r' if actual == prediction[0] else 'w'] = stats['r' if actual == prediction[0] else 'w'] + 1
                pct_correct = (1.0 * stats['r'] / (stats['r'] + stats['w']))
                all_output = all_output + str(('stats', self.name, round(pct_correct, 2)))
                all_output = all_output + str(('stats_debug', stats))
                self.percent_correct = int(pct_correct * 100)
                self.prediction_size = len(test_data[0])

            all_output = all_output + str((self.name, round(score * 100)))
            self.score = score * 100
            end_time = int(time.time())
            self.time = end_time - start_time
            self.output = all_output

        self.clf = clf

        return clf

    def predict(self, sample):
        last_sample = sample[-1]
        nn_price = 0.00
        sample = StandardScaler().fit_transform(sample)
        recommend = self.clf.predict(sample)
        recommend_str = 'HOLD' if recommend[0] == ClassifierTest.HOLD else (
            'BUY' if recommend[0] == ClassifierTest.BUY else 'SELL')
        projected_change_pct = 0.00
        return recommend_str, nn_price, last_sample, projected_change_pct

    def graph_url(self):
        return '/static/' + str(self.pk) + '.png'

    def graph_link(self):
        return '<a href={}>graph</a>'.format(self.graph_url())

    def graph(self, filename):
        figure = plt.figure(figsize=(27, 9))
        figure.max_num_figures = 5
        matplotlib.figure.max_num_figures = 5
        i = 0
        cm = plt.cm.RdBu
        cm_bright = ListedColormap(['#00FF00', '#FF0000', '#0000FF'])
        ax = plt.subplot(1, 1, i)
        # Plot the training points
        ax.scatter(self.X_train[:, 0], self.X_train[:, 1], c=self.y_train, cmap=cm_bright)
        # and testing points
        ax.scatter(self.X_test[:, 0], self.X_test[:, 1], c=self.y_test, cmap=cm_bright, alpha=0.6)
        ax.set_xlim(self.xz[0].min(), self.xz[0].max())
        ax.set_ylim(self.xz[1].min(), self.xz[1].max())
        ax.set_xticks(())
        ax.set_yticks(())

        self.Z = self.clf.predict(self._input)
        self.Z = self.Z.reshape(self.xz[0].shape)
        ax.contourf(self.xz[0], self.xz[1], self.Z, cmap=cm, alpha=.8)

        # Plot also the training points
        ax.scatter(self.X_train[:, 0], self.X_train[:, 1], c=self.y_train, cmap=cm_bright)
        # and testing points
        ax.scatter(self.X_test[:, 0], self.X_test[:, 1], c=self.y_test, cmap=cm_bright,
                   alpha=0.6)

        ax.set_xlim(self.xz[0].min(), self.xz[0].max())
        ax.set_ylim(self.xz[1].min(), self.xz[1].max())
        ax.set_xticks(())
        ax.set_yticks(())
        ax.set_title("(" + self.name + ")")
        text = ('%.2f' % self.score).lstrip('0')
        ax.text(self.xz[0].max() - .3, self.xz[1].min() + .3, text,
                size=15, horizontalalignment='right')
        i += 1
        filepath = settings.BASE_DIR + filename
        figure.subplots_adjust(left=.02, right=.98)
        figure.savefig(filepath, dpi=100)


class PredictionTest(AbstractedTesterClass):
    type = models.CharField(max_length=30, default='mock', db_index=True)
    symbol = models.CharField(max_length=30, db_index=True)
    percent_correct = models.FloatField(null=True)
    avg_diff = models.FloatField(null=True)
    datasetinputs = models.IntegerField()
    hiddenneurons = models.IntegerField()
    granularity = models.IntegerField()
    minutes_back = models.IntegerField(default=0)
    time = models.IntegerField(default=0)
    epochs = models.IntegerField(default=0)
    prediction_size = models.IntegerField(default=0)
    learningrate = models.FloatField(default=0)
    momentum = models.FloatField(default=0)
    weightdecay = models.FloatField(default=0)
    bias = models.BooleanField(default=False)
    bias_chart = models.IntegerField(default=-1)
    recurrent = models.BooleanField(default=False)
    recurrent_chart = models.IntegerField(default=-1)
    profitloss = models.FloatField(default=0)
    profitloss_int = models.IntegerField(default=0)
    timedelta_back_in_granularity_increments = models.IntegerField(default=0)
    output = models.TextField()

    def __str__(self):
        return self.symbol + " on " + str(self.created_on)

    def rerun(self, keep_new_obj=False):
        from history.predict import predict_v2
        try:
            pk = predict_v2(self.symbol,
                            hidden_layers=self.hiddenneurons,
                            NUM_MINUTES_BACK=self.minutes_back,
                            NUM_EPOCHS=self.epochs,
                            granularity_minutes=self.granularity,
                            datasetinputs=self.datasetinputs,
                            learningrate=self.learningrate,
                            bias=self.bias,
                            momentum=self.momentum,
                            weightdecay=self.weightdecay,
                            recurrent=self.recurrent)
            pt = PredictionTest.objects.get(pk=pk)
            if not keep_new_obj:
                pt.delete()
            else:
                return pt.pk
        except Exception as e:
            print(e)

    def related_mocks(self):
        days_ago = 2
        return PredictionTest.objects.filter(created_on__gt=(timezone.now() - datetime.timedelta(days=int(days_ago))),
                                             symbol=self.symbol,
                                             hiddenneurons=self.hiddenneurons,
                                             minutes_back=self.minutes_back,
                                             epochs=self.epochs,
                                             granularity=self.granularity,
                                             datasetinputs=self.datasetinputs,
                                             learningrate=self.learningrate,
                                             bias=self.bias,
                                             momentum=self.momentum,
                                             weightdecay=self.weightdecay,
                                             recurrent=self.recurrent,
                                             type='mock')

    def create_DS(self, data):
        size = self.datasetinputs
        DS = SupervisedDataSet(size, 1)
        try:
            for i, val in enumerate(data):
                sample = create_sample_row(data, i, size)
                target = data[i + size]
                DS.addSample(sample, (target,))
        except Exception as e:
            if "list index out of range" not in str(e):
                print(e)
        return DS

    def get_nn(self, train=True):

        train_data, results_data = self.get_train_and_test_data()
        DS = self.create_DS(train_data)

        try:
            import arac  # noqa
            print("ARAC Available, using fast mode network builder!")
            FNN = buildNetwork(DS.indim, self.hiddenneurons, DS.outdim, bias=self.bias, recurrent=self.recurrent,
                               fast=True)
        except ImportError:
            FNN = buildNetwork(DS.indim, self.hiddenneurons, DS.outdim, bias=self.bias, recurrent=self.recurrent)
        FNN.randomize()

        TRAINER = BackpropTrainer(FNN, dataset=DS, learningrate=self.learningrate,
                                  momentum=self.momentum, verbose=False, weightdecay=self.weightdecay)

        if train:
            for i in range(self.epochs):
                TRAINER.train()

        self.nn = FNN
        return FNN

    def recommend_trade(self, nn_price, last_sample, fee_amount=get_fee_amount()):
        fee_amount = fee_amount * 2  # fee x 2 since we'd need to clear both buy and sell fees to be profitable
        fee_amount = fee_amount * settings.FEE_MANAGEMENT_STRATEGY  # see desc in settings.py
        anticipated_percent_increase = (nn_price - last_sample) / last_sample
        if abs(anticipated_percent_increase) < fee_amount:
            should_trade = 'HOLD'
        elif anticipated_percent_increase > fee_amount:
            should_trade = 'BUY'
        elif anticipated_percent_increase < fee_amount:
            should_trade = 'SELL'
        return should_trade

    def predict(self, sample):
        last_sample = sample[-1]
        nn_price = self.nn.activate(sample)
        recommend = self.recommend_trade(nn_price, last_sample)
        projected_change_pct = (nn_price - last_sample) / last_sample
        return recommend, nn_price, last_sample, projected_change_pct


class SocialNetworkMention(AbstractedTesterClass):
    network_name = models.CharField(max_length=30, db_index=True)
    network_username = models.CharField(max_length=100)
    network_id = models.CharField(default=0, max_length=100, db_index=True)
    network_created_on = models.DateTimeField()
    symbol = models.CharField(max_length=30, db_index=True)
    text = models.TextField()
    sentiment_polarity = models.FloatField(default=0.00)
    sentiment_subjectivity = models.FloatField(default=0.00)

    def set_sentiment(self):
        sentiment = textblob.TextBlob(self.text).sentiment
        self.sentiment_polarity = sentiment.polarity
        self.sentiment_subjectivity = sentiment.subjectivity
