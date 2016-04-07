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

        pool = Pool(settings.NUM_THREADS)
        conf = settings.TRAINER_CURRENCY_CONFIG['classifiers']
        print("Starting SK run")
        for ticker in conf['ticker']:
            for min_back in conf['min_back']:
                for granularity in conf['granularity']:
                    for datasetinputs in conf['datasetinputs']:
                        for timedelta_back_in_granularity_increments in \
                                conf['timedelta_back_in_granularity_increments']:
                            for name in conf['name']:
                                pool.apply_async(do_classifier_test, args=(
                                    name,
                                    ticker,
                                    datasetinputs,
                                    granularity,
                                    min_back,
                                    timedelta_back_in_granularity_increments
                                ), callback=self._log_results)
        print("All SK jobs queued")
        pool.close()
        pool.join()
        print("SK run complete")
        for result in self.result_list:
            print(result)
