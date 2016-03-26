from django.core.management.base import BaseCommand
from history.predict import predict_v2
from history.tools import print_and_log
class Command(BaseCommand):

    help = 'tests various settings that could make the NN more accurate'

    def handle(self, *args, **options):
        # http://scikit-learn.org/stable/auto_examples/classification/plot_classifier_comparison.html
        import numpy as np
        import matplotlib.pyplot as plt
        from matplotlib.colors import ListedColormap
        from sklearn.cross_validation import train_test_split
        from sklearn.preprocessing import StandardScaler
        from sklearn.datasets import make_moons, make_circles, make_classification
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.svm import SVC
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
        from sklearn.naive_bayes import GaussianNB
        from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
        from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

        h = .02  # step size in the mesh

        names = ["Nearest Neighbors", "Linear SVM", "RBF SVM", "Decision Tree",
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

        X, y = make_classification(n_features=2, n_redundant=0, n_informative=2,
                                   random_state=1, n_clusters_per_class=1)
        rng = np.random.RandomState(2)
        X += 2 * rng.uniform(size=X.shape)
        linearly_separable = (X, y)


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
                    price_datasets[0].append(sample)
                    price_datasets[1].append(do_buy)
                except Exception as e:
                    print(e)
            datasets.append(price_datasets)
            _names.append(str(gran))


        if graph:
            figure = plt.figure(figsize=(27, 9))
        i = 1
        # iterate over datasets
        for _index in range(0,len(datasets)):
            ds = datasets[_index]
            # preprocess dataset, split into training and test part
            X, y = ds
            X = StandardScaler().fit_transform(X)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.4)

            x_min, x_max = X[:, 0].min() - .5, X[:, 0].max() + .5
            y_min, y_max = X[:, 1].min() - .5, X[:, 1].max() + .5
            xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                                 np.arange(y_min, y_max, h))

            # just plot the dataset first
            if graph:
                cm = plt.cm.RdBu
                cm_bright = ListedColormap(['#FF0000', '#0000FF'])
                ax = plt.subplot(len(datasets), len(classifiers) + 1, i)
                # Plot the training points
                ax.scatter(X_train[:, 0], X_train[:, 1], c=y_train, cmap=cm_bright)
                # and testing points
                ax.scatter(X_test[:, 0], X_test[:, 1], c=y_test, cmap=cm_bright, alpha=0.6)
                ax.set_xlim(xx.min(), xx.max())
                ax.set_ylim(yy.min(), yy.max())
                ax.set_xticks(())
                ax.set_yticks(())
            i += 1

            # iterate over classifiers
            for name, clf in zip(names, classifiers):
                if graph:
                    ax = plt.subplot(len(datasets), len(classifiers) + 1, i)
                clf.fit(X_train, y_train)
                score = clf.score(X_test, y_test)
                # Plot the decision boundary. For that, we will assign a color to each
                # point in the mesh [x_min, m_max]x[y_min, y_max].
                _input = np.c_[xx.ravel(), yy.ravel()]
                if hasattr(clf, "decision_function"):
                    Z = clf.decision_function(_input)
                else:
                    Z = clf.predict_proba(_input)[:, 1]

                print(name,round(score*100))
                # Put the result into a color plot
                if graph:
                    Z = Z.reshape(xx.shape)
                    ax.contourf(xx, yy, Z, cmap=cm, alpha=.8)

                    # Plot also the training points
                    ax.scatter(X_train[:, 0], X_train[:, 1], c=y_train, cmap=cm_bright)
                    # and testing points
                    ax.scatter(X_test[:, 0], X_test[:, 1], c=y_test, cmap=cm_bright,
                               alpha=0.6)

                    ax.set_xlim(xx.min(), xx.max())
                    ax.set_ylim(yy.min(), yy.max())
                    ax.set_xticks(())
                    ax.set_yticks(())
                    ax.set_title("("+_names[_index]+")"+name)
                    text  = ('%.2f' % score).lstrip('0')
                    ax.text(xx.max() - .3, yy.min() + .3, text,
                            size=15, horizontalalignment='right')
                    i += 1

                stats = { 'r' : 0, 'w' :0 }
                for ds in datasets:
                    for i in range(0,len(ds[0])):
                        sample = ds[0][i]
                        actual = ds[1][i]
                        prediction = clf.predict(sample)
                        stats['r' if actual == prediction[0] else 'w'] =stats['r' if actual == prediction[0] else 'w'] + 1
                print('stats',name,stats,round((100.0*stats['r']/(stats['r']+stats['w'])),2))


        if graph:
            figure.subplots_adjust(left=.02, right=.98)
            plt.show()

