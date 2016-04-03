from django.core.management.base import BaseCommand
from history.models import ClassifierTest
from django.conf import settings
from history.tools import print_and_log
from multiprocessing import Pool


def do_classifier_test(name, ticker, data_set_inputs, granularity, min_back, timedelta_back):
    try:
        ct = ClassifierTest(name=name,
                            type='mock',
                            symbol=ticker,
                            datasetinputs=data_set_inputs,
                            granularity=granularity,
                            minutes_back=min_back,
                            timedelta_back_in_granularity_increments=timedelta_back)
        ct.get_classifier()
        ct.save()
        return_data = "(ct) {} {} {} {} {} {} returned {}% correct ".format(name, ticker, data_set_inputs,
                                                                            granularity,
                                                                            min_back,
                                                                            timedelta_back,
                                                                            ct.percent_correct)

        print_and_log(return_data)
        # Hack to only graph successful charts, until we figure out this warning
        # http://bits.owocki.com/010Z1M3d170p/Image%202016-03-02%20at%208.30.17%20AM.png
        if ct.percent_correct > 60 or not settings.MAKE_TRADES:
            ct.graph(ct.graph_url())
        return return_data
    except Exception as e:
        return "Exception in {} {} {} {} {} {}: {}".format(name, ticker, data_set_inputs,
                                                           granularity,
                                                           min_back,
                                                           timedelta_back,
                                                           str(e))


class Command(BaseCommand):

    help = 'tests various settings that could make the NN more accurate'
    result_list = []

    def _log_results(self, result):
        self.result_list.append(result)

    def handle(self, *args, **options):

        ticker_options = ['BTC_ETH', 'USDT_BTC']

        min_back_options = [100, 1000, 24 * 60, 24 * 60 * 2]

        granularity_options = [10, 15, 20, 30, 40, 50, 60, 120, 240]
        if not settings.MAKE_TRADES:
            granularity_options = [1]

        datasetinput_options = [2]
        # TODO: enable more than just 1 type

        # sets how far apart (in granularity increments) the datasets are
        timedelta_back_in_granularity_increments_options = [10, 30, 60, 100, 1000]

        name_options = ["Nearest Neighbors", "Linear SVM", "RBF SVM", "Decision Tree",
                        "Random Forest", "AdaBoost", "Naive Bayes", "Linear Discriminant Analysis",
                        "Quadratic Discriminant Analysis"]

        pool = Pool(settings.NUM_THREADS)

        print("Starting SK Run")
        for ticker in ticker_options:
            for min_back in min_back_options:
                for granularity in granularity_options:
                    for datasetinputs in datasetinput_options:
                        for timedelta_back_in_granularity_increments in \
                                timedelta_back_in_granularity_increments_options:
                            for name in name_options:
                                pool.apply_async(do_classifier_test, args=(
                                    name,
                                    ticker,
                                    datasetinputs,
                                    granularity,
                                    min_back,
                                    timedelta_back_in_granularity_increments
                                ), callback=self._log_results)
        print("All SK Jobs queues")
        pool.close()
        pool.join()
        print("SK Run Complete")
        print(self.result_list)