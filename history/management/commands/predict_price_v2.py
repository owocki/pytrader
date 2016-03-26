from django.core.management.base import BaseCommand
from history.predict import predict_v2

class Command(BaseCommand):

    help = 'predicts a price'
    args = "ticker"
    # based upon http://stackoverflow.com/questions/25845557/pybrain-neural-network-for-stock-prediction-wont-learn

    def handle(self, *args, **options):
        ticker = args[0]
        print("****** STARTING PREDICTOR " + ticker + " ******* ")
        predict_v2(ticker,recurrent=False,datasetinputs=2)
