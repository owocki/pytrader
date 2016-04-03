from django.core.management.base import BaseCommand
from history.predict import predict_v2
from django.conf import settings
from history.tools import print_and_log
from multiprocessing import Pool


class Command(BaseCommand):

    help = 'tests various settings that could make the NN more accurate'

    def handle(self, *args, **options):
        ticker_options = ['BTC_ETH','USDT_BTC']
        hidden_layer_options = [1,5, 15, 40] 
        # 2/23 -- removed 15, it was barely edged out by 1,5.
        # 2/25 -- added 15, 40 in because of recent bugs
        
        min_back_options = [100,1000,24*60,24*60*2] 
        # 2/22 - eliminated 10000 
        # 2/25 -- added 24*50, 24*60*2 because "maybe because NN only contains last 1000 data points (1/3 day).
        #   if only selling happened during that time, nn will bias towards selling.  duh!"
        
        granularity_options = [10, 15, 20, 30, 40, 50, 60, 120,240] 
        # 2/23 notes - results so far: 59 (54% correct) 15 (56% correct) 1 (50% correct) 5 (52% correct).
        #   removing 1,5, adding 30 . 2/23 (pt 2) -- added 119, 239
        # 2/24 notes -- removed 120,240, added 20, 40, 45
        # 2/25 notes -- added 10, 50, removed 45
        # 2/25 -- added 120,240 back in to retest in light of recent bugs

        datasetinput_options = [1,2,3,4,5,6, 15,10,20,40,100, 200] 
        # 2/23 -- removed 3,5,15 -- added 20,40,100
        # 2/24 -- removed 7,10,20,40,100, added 3,4,5
        # 2/25 -- added 3,5,15,10,20,40,100 back in to retest in light of recent bugs

        epoch_options = [1000] 
        # 2/22 -- eliminated 4000, 100
        
        bias_options = [True] 
        # 2/22 -- Eliminated 'False'
        
        momentum_options = [0.1]
        
        learningrate_options = [0.05] 
        # 2/22 -- elimated 0.005, 0.01, adding 0.03 and 0.1 today.  #2/23 - 0.1 (54% correct) 0.05 (55% correct) 0.03
        # (54% correct) .  eliminating everything but 0.05 so i can test more #datasetinput_options
        
        weightdecay_options = [0.0] 
        # 2/22 -- eliminated 0.1,0.2
        
        recurrent_options = [True] 
        # 2/23 notes - 0 (52% correct) 1 (55% correct), removed false

        # sets how far apart (in granularity increments) the data sets are
        timedelta_back_in_granularity_increments_options = [10,30,60,100,1000]

        pool = Pool(settings.NUM_THREADS)

        print("Starting V2 Run")
        for ticker in ticker_options:
            for hidden_layers in hidden_layer_options:
                for min_back in min_back_options:
                    for epochs in epoch_options:
                        for granularity in granularity_options:
                            for datasetinputs in datasetinput_options:
                                for bias in bias_options:
                                    for momentum in momentum_options:
                                        for learningrate in learningrate_options:
                                            for weightdecay in weightdecay_options:
                                                for recurrent in recurrent_options:
                                                    for timedelta_back_in_granularity_increments in \
                                                            timedelta_back_in_granularity_increments_options:
                                                        pool.apply_async(self._do_classifier_test, args=(
                                                            ticker, hidden_layers, min_back, epochs, granularity,
                                                            datasetinputs,
                                                            learningrate, bias, momentum, recurrent, weightdecay,
                                                            timedelta_back_in_granularity_increments
                                                        ))
        print("All V2 jobs queued")
        pool.close()
        pool.join()
        print("V2 Run Complete")

    @staticmethod
    def _do_classifier_test(ticker, hidden_layers, min_back, epochs, granularity, datasetinputs,
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