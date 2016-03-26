from __future__ import print_function
from django.core.management.base import BaseCommand
from pybrain.datasets import SequentialDataSet
from itertools import cycle
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure.modules import LSTMLayer
from pybrain.supervised import RPropMinusTrainer
from sys import stdout
from history.models import Price
from history.tools import normalization


NUM_MINUTES_BACK=300
MULT_FACTOR=100    

class Command(BaseCommand):

    help = 'predicts a price'
    args = "ticker"
    # based upon http://stackoverflow.com/questions/25967922/pybrain-time-series-prediction-using-lstm-recurrent-nets

    def handle(self, *args, **options):
        ticker = args[0]
        print("****** STARTING PREDICTOR " + ticker + " ******* ")
        prices = Price.objects.filter(symbol=ticker).order_by('-created_on').values_list('price',flat=True)
        data = normalization(list(prices[0:NUM_MINUTES_BACK].reverse()))
        data = [ int(x * MULT_FACTOR) for x in data]
        ds = SequentialDataSet(1, 1)
        for sample, next_sample in zip(data, cycle(data[1:])):
            ds.addSample(sample, next_sample)

        net = buildNetwork(1, 5, 1, 
                           hiddenclass=LSTMLayer, outputbias=False, recurrent=True)

        trainer = RPropMinusTrainer(net, dataset=ds)
        train_errors = [] # save errors for plotting later
        EPOCHS_PER_CYCLE = 5
        CYCLES = 100
        EPOCHS = EPOCHS_PER_CYCLE * CYCLES
        for i in xrange(CYCLES):
            trainer.trainEpochs(EPOCHS_PER_CYCLE)
            train_errors.append(trainer.testOnData())
            epoch = (i+1) * EPOCHS_PER_CYCLE
            print("\r epoch {}/{}".format(epoch, EPOCHS), end="")
            stdout.flush()

        print()
        print("final error =", train_errors[-1])

        for sample, target in ds.getSequenceIterator(0):
            show_pred_sample = net.activate(sample) / MULT_FACTOR
            show_sample = sample / MULT_FACTOR
            show_target = target / MULT_FACTOR
            show_diff = show_pred_sample - show_target
            show_diff_pct = 100 * show_diff / show_pred_sample
            print("{} => {}, act {}. ({}%)".format(show_sample[0],round(show_pred_sample[0],3),show_target[0],int(round(show_diff_pct[0],0))))
