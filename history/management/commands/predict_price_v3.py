from django.core.management.base import BaseCommand
from history.tools import normalization
from history.models import Price
from pybrain.datasets import SupervisedDataSet
from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer

NUM_MINUTES_BACK=60

class Command(BaseCommand):

    help = 'predicts a price'
    args = "ticker"
    # based upon http://stackoverflow.com/questions/25439910/pybrain-lstm-sequence-to-predict-sequential-data

    def handle(self, *args, **options):
        ticker = args[0]
        print("****** STARTING PREDICTOR " + ticker + " ******* ")
        #prices = Price.objects.filter(symbol=ticker).order_by('-created_on').values_list('price',flat=True)
        #data = prices[0:NUM_MINUTES_BACK].reverse()
        #data = [ x * MULT_FACTOR for x in data]

        from pybrain.tools.shortcuts import buildNetwork
        from pybrain.supervised.trainers import BackpropTrainer
        from pybrain.datasets import SequentialDataSet
        from pybrain.structure import SigmoidLayer, LinearLayer
        from pybrain.structure import LSTMLayer

        import itertools
        import numpy as np

        INPUTS = 5
        OUTPUTS = 1
        HIDDEN = 40

        net = buildNetwork(INPUTS, HIDDEN, OUTPUTS, hiddenclass=LSTMLayer, outclass=LinearLayer, recurrent=True, bias=True) 

        ds = SequentialDataSet(INPUTS, OUTPUTS)
        ds.addSample([0,1,2,3,4],[5])
        ds.addSample([5,6,7,8,9],[10])
        ds.addSample([10,11,12,13,14],[15])
        ds.addSample([16,17,18,19,20],[21])

        net.randomize()

        trainer = BackpropTrainer(net, ds)

        for _ in range(1000):
            trainer.train()

        x=net.activate([0,1,2,3,4])
        print x 
