from django.core.management.base import BaseCommand
from history.predict import predict_v2
from django.conf import settings
from history.tools import print_and_log
from multiprocessing import Pool


def do_prediction_test(ticker, hidden_layers, min_back, epochs, granularity, datasetinputs,
                       learningrate, bias, momentum, recurrent, weightdecay,
                       timedelta_back_in_granularity_increments):
    try:
        predict_v2(ticker,
                   hidden_layers=hidden_layers,
                   NUM_MINUTES_BACK=min_back,
                   NUM_EPOCHS=epochs,
                   granularity_minutes=granularity,
                   datasetinputs=datasetinputs,
                   learningrate=learningrate,
                   bias=bias,
                   momentum=momentum,
                   recurrent=recurrent,
                   weightdecay=weightdecay,
                   timedelta_back_in_granularity_increments=timedelta_back_in_granularity_increments)
    except Exception as e:
        print_and_log("(p)" + str(e))


class Command(BaseCommand):

    help = 'tests various settings that could make the NN more accurate'

    def handle(self, *args, **options):

        pool = Pool(settings.NUM_THREADS)
        conf = settings.TRAINER_CURRENCY_CONFIG['supervised_nn']

        print("Starting V2 run")
        for ticker in conf['ticker']:
            for hidden_layers in conf['hidden_layers']:
                for min_back in conf['min_back']:
                    for epochs in conf['epochs']:
                        for granularity in conf['granularity']:
                            for datasetinputs in conf['datasetinputs']:
                                for bias in conf['bias']:
                                    for momentum in conf['momentum']:
                                        for learningrate in conf['learningrate']:
                                            for weightdecay in conf['weightdecay']:
                                                for recurrent in conf['recurrent']:
                                                    for timedelta_back_in_granularity_increments in \
                                                            conf['timedelta_back_in_granularity_increments']:
                                                        pool.apply_async(do_prediction_test, args=(
                                                            ticker, hidden_layers, min_back, epochs, granularity,
                                                            datasetinputs,
                                                            learningrate, bias, momentum, recurrent, weightdecay,
                                                            timedelta_back_in_granularity_increments
                                                        ))
        print("All V2 jobs queued")
        pool.close()
        pool.join()
        print("V2 run complete")
