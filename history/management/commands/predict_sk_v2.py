from django.core.management.base import BaseCommand
from history.predict import predict_v2
from history.tools import print_and_log
class Command(BaseCommand):

    help = 'tests various settings that could make the NN more accurate'

    def handle(self, *args, **options):
        #http://scikit-learn.org/stable/auto_examples/classification/plot_classification_probability.html

        from history.tools import normalization, filter_by_mins, create_sample_row
        from history.models import Price

        graph = False
        self.symbol ='BTC_ETH'
        self.minutes_back = 100
        self.timedelta_back_in_granularity_increments = 0
        datasetinputs = 2
        gran_options = [1,5,15,30]
        gran_options = [30,60,120,240]
        datasets = []
        _names = []
        for gran in gran_options:
            self.granularity = gran

            splice_point = self.minutes_back + self.timedelta_back_in_granularity_increments
            prices = Price.objects.filter(symbol=self.symbol).order_by('-created_on')
            prices = filter_by_mins(prices,self.granularity)
            prices = [price.price for price in prices]
            data = normalization(list(prices[0:splice_point]))
            data.reverse()

            price_datasets = [[],[]]
            for i,val in enumerate(data):
                try:
                    # get NN projection
                    sample = create_sample_row(data,i,datasetinputs)
                    last_price = data[i+datasetinputs-1]
                    next_price = data[i+datasetinputs]
                    change =  next_price - last_price
                    pct_change = change / last_price
                    fee_pct = 0.002
                    do_buy = -1 if abs(pct_change) < fee_pct and False else (1 if change > 0 else 0)
                    price_datasets[0].append([x for x in sample])
                    price_datasets[1].append(do_buy)
                except Exception as e:
                    print(e)
            datasets.append(price_datasets)
            _names.append(str(gran))
            _datasets = datasets

            # Author: Alexandre Gramfort <alexandre.gramfort@inria.fr>
            # License: BSD 3 clause

            import matplotlib.pyplot as plt
            import numpy as np

            from sklearn.linear_model import LogisticRegression
            from sklearn.svm import SVC
            from sklearn import datasets

            iris = datasets.load_iris()
            X = iris.data[:, 0:2]  # we only take the first two features for visualization
            y = iris.target

            _datasets = _datasets[0]
            X = np.ndarray(shape=(len(_datasets[0]),2), dtype=float, buffer = np.array(_datasets[0]) )  
            y = np.array(_datasets[1])

            n_features = X.shape[1]

            C = 1.0

            # Create different classifiers. The logistic regression cannot do
            # multiclass out of the box.
            classifiers = {'L1 logistic': LogisticRegression(C=C, penalty='l1'),
                           'L2 logistic (OvR)': LogisticRegression(C=C, penalty='l2'),
                           'Linear SVC': SVC(kernel='linear', C=C, probability=True,
                                             random_state=0),
                           'L2 logistic (Multinomial)': LogisticRegression(
                            C=C, solver='lbfgs', multi_class='multinomial'
                            )}

            n_classifiers = len(classifiers)

            plt.figure(figsize=(3 * 2, n_classifiers * 2))
            plt.subplots_adjust(bottom=.2, top=.95)

            xx = np.linspace(3, 9, 100)
            yy = np.linspace(1, 5, 100).T
            xx, yy = np.meshgrid(xx, yy)
            Xfull = np.c_[xx.ravel(), yy.ravel()]

            for index, (name, classifier) in enumerate(classifiers.items()):
                classifier.fit(X, y)

                y_pred = classifier.predict(X)
                classif_rate = np.mean(y_pred.ravel() == y.ravel()) * 100
                print("classif_rate for %s : %f " % (name, classif_rate))

                # View probabilities=
                probas = classifier.predict_proba(Xfull)
                n_classes = np.unique(y_pred).size
                for k in range(n_classes):
                    plt.subplot(n_classifiers, n_classes, index * n_classes + k + 1)
                    plt.title("Class %d" % k)
                    if k == 0:
                        plt.ylabel(name)
                    imshow_handle = plt.imshow(probas[:, k].reshape((100, 100)),
                                               extent=(3, 9, 1, 5), origin='lower')
                    plt.xticks(())
                    plt.yticks(())
                    idx = (y_pred == k)
                    if idx.any():
                        plt.scatter(X[idx, 0], X[idx, 1], marker='o', c='k')

            ax = plt.axes([0.15, 0.04, 0.7, 0.05])
            plt.title("Probability")
            plt.colorbar(imshow_handle, cax=ax, orientation='horizontal')

            plt.show()
