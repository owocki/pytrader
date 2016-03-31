from django.core.management.base import BaseCommand
from history.models import ClassifierTest
from django.conf import settings
from history.tools import print_and_log


class Command(BaseCommand):

    help = 'tests various settings that could make the NN more accurate'

    def handle(self, *args, **options):

        ticker_options = ['BTC_ETH', 'USDT_BTC']

        min_back_options = [100, 1000, 24 * 60, 24 * 60 * 2]

        granularity_options = [10, 15, 20, 30, 40, 50, 60, 120, 240]
        if not settings.MAKE_TRADES:
            granularity_options = [1]

        datasetinput_options = [2]
        # TODO: enable more than just 1 type

        timedelta_back_in_granularity_increments_options = [10, 30, 60, 100, 1000]  # sets how far apart (in granularity increments) the datasets are

        name_options = ["Nearest Neighbors", "Linear SVM", "RBF SVM", "Decision Tree",
                        "Random Forest", "AdaBoost", "Naive Bayes", "Linear Discriminant Analysis",
                        "Quadratic Discriminant Analysis"]

        for ticker in ticker_options:
            for min_back in min_back_options:
                for granularity in granularity_options:
                    for datasetinputs in datasetinput_options:
                        for timedelta_back_in_granularity_increments in timedelta_back_in_granularity_increments_options:
                            for name in name_options:
                                try:
                                    ct = ClassifierTest(name=name,
                                                        type='mock',
                                                        symbol=ticker,
                                                        datasetinputs=datasetinputs,
                                                        granularity=granularity,
                                                        minutes_back=min_back,
                                                        timedelta_back_in_granularity_increments=timedelta_back_in_granularity_increments)
                                    ct.get_classifier()
                                    ct.save()
                                    print_and_log("(ct) {} {} {} {} {} {} returned {}% corrrect ".format(name, symbol, datasetinputs, granularity, minutes_back, timedelta_back_in_granularity_increments, ct.percent_correct))
                                    if ct.percent_correct > 60 or not settings.MAKE_TRADES:  # hack to only graph successful charts, until we figure out this warning http://bits.owocki.com/010Z1M3d170p/Image%202016-03-02%20at%208.30.17%20AM.png
                                        ct.graph(ct.graph_url())
                                except Exception as e:
                                    print("exception:" + str(e))
