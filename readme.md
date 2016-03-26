

# pytrader

pytrader is a _cryptocurrency_ trading robot programmed to work on the [poloniex.com cryptocurrency platform.](http://poloniex.com).

I built this as a side project in January / February 2016, as a practical means of getting some experience with machine learning, quantitative finance, and of course hopefully making some profit `;)`.

--- 

__3/26/2016__ - My test portfolio was initialized with a 1 BTC deposit, and after 2 months and 23,413 trades,  exited with 0.955 BTC.  The system paid 2.486 BTC in fees to poloniex.  CALL TO ACTION -- Get this trader to profitability.    [A strategy is being fleshed out here](https://github.com/owocki/pytrader/issues/1).

--- 

## How

pytrader uses _pybrain_ and _sklearn_ to make trade ( buy/sell/hold decisions ), and then acts upon them. 

### 1. sklearn classifiers

Supported classifiers are as follows:

```["Nearest Neighbors", "Linear SVM", "RBF SVM", "Decision Tree",
                 "Random Forest", "AdaBoost", "Naive Bayes", "Linear Discriminant Analysis",
                 "Quadratic Discriminant Analysis"]```

Here's an example of a *Decision Tree* classifier being used to make a buy (blue), sell (red), or hold(green) decision on the [BTC_ETH pair](https://www.poloniex.com/exchange#btc_eth).

<img src='http://bits.owocki.com/1l3K0W3P1g0A/211224.png' />

and here's a *Naive Bayes* decision tree for the [USDT_BTC pair](https://www.poloniex.com/exchange#usdt_btc)

<img src=http://bits.owocki.com/3f2E38052p0J/238365.png />

On both graphs, the x axis is a recent price movement, and the y axis is a previous price movement, the length of which is determined by a parameter called *granularity*.  These graphs show only the last two price movements. The graphing library used is constrained by two dimensional space, but you could generate a classifier that acts upon *n* pricemovements ( *n* dimensional space ).

There are many many different parameters one could use to train a *ClassifierTest*.  This problem space is enumerated by the management command *predict_many_sk.py*.  For each permutation of parameters, a _percent_correct_ value is generated against actual price movement data.  Using this brute force methodology, we are able to discover which classifiers are up for the job of trading.

By testing and tuning various parameters to to the *ClassifierTest*, I was able to consistently predict buy/sell/hold movements between 55-65% of the time, depending upon the currency pair and parameters to the test.

### 2. pybrain neural networks

In addition to using sklearn Classifiers, Pybrain Supervised Learning tools were used to predict price movement.  This is represented in the data model as a *PredictionTest*, and the problem space is enumerated in *predict_many_v2.py*.   By testing and tuning various parameters in the pybrain NN,  I was able to consistently predict directional price movements around 55% of the time.

### Database model

<img src='http://bits.owocki.com/373h1z2l2V3x/download.png' />

## Administration & Optimization

Administration of this tool is primarily done through the django admin.  

There's a series of graphs in the admin that show trades, and portfolio profitability over time.

<img src='http://bits.owocki.com/3q2M3u0i3L2g/Image%202016-03-26%20at%209.22.23%20AM.png' />

<img src='http://bits.owocki.com/2a1M292b1E3X/Image%202016-03-26%20at%209.21.16%20AM.png' />

... and allow the graphical debugging of trade decisions ... 

<img src='http://bits.owocki.com/0N2z260s0e3p/Image%202016-03-26%20at%209.30.04%20AM.png' />

... and allow the tuning of `PredictionTests`  and `ClassifierTests`  ...

<img src='http://bits.owocki.com/0m3e1i0u0e0a/Image%202016-03-26%20at%209.22.55%20AM.png' />

by each of the native pybrain (Prediction Test) and sklearn (ClassiferTests) parameters ..

<img src='http://bits.owocki.com/3D3k441p441Q/Image%202016-03-26%20at%209.23.37%20AM.png' />

Once a NN or classifier is found that is better than what is being used, *trade.py* is updated with the most profitable configurations.

```
        self.predictor_configs = [
            {'type' : 'nn',
                'name' : 'ETH / 5',
                'symbol': 'BTC_ETH',
                'weight' : 0.1,
                'granularity' : granularity,
                'datasetinputs': 5},
            {'type' : 'nn',
                'name' : 'ETH / 5',
                'symbol': 'BTC_ETH',
                'weight' : 0.1,
                'granularity' : granularity,
                'datasetinputs': 4},
            {'type' : 'classifier',
                'symbol': 'USDT_BTC',
                'name' : 'AdaBoost',
                'weight' : 0.1,
                'granularity' : granularity,
                'datasetinputs' : 2,
                'minutes_back': 1000},
            {'type' : 'classifier',
                'symbol': 'USDT_BTC',
                'name' : 'Naive Bayes',
                'weight' : 0.1,
                'granularity' : granularity,
                'datasetinputs' : 2,
                'minutes_back': 1000},
            {'type' : 'classifier',
                'symbol': 'BTC_ETH',
                'name' : 'Naive Bayes',
                'weight' : 2,
                'granularity' : granularity * 3,
                'datasetinputs' : 2,
                'minutes_back': 1000},
        ]
```

### trade.py

*trade.py* is the system's always-running trading engine.  At a high level, it creates & trains ClassifierTests and PredictionTests based upon the most profitable indicators.  Once those Tests are trained, it runs a loop that makes trades based upon them if a certain confidence threshold is reached amongst its `self.predictor_configs` .

## Why open source this?

Although I am able to predict price movements with some degree of accuracy that beats random, I was never able to generate a robot that traded profitably *after fees*.  [Especially after poloniex changed their fee structure](https://poloniex.com/fees/)

My test portfolio was initialized with a 1 BTC deposit, and after 2 months and 23,413 trades,  exited with 0.955 BTC.  The system paid 2.486 BTC in fees to poloniex.  

The code is not perfect.  This was a pre-product/market-fit side project. Please feel free to open an _Issue_ if you do not understand something.

## Deployment

After you've cloned the repo, you'll want to create a *local_settings.py* file with the following information in it:

```
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAKE_TRADES=False

API_KEY="<POLO_API_KEY>"
API_SECRET="<POLO_SECRET>"

```

install your requirements

``` 
pip install -r requirements.txt
```

set up your database..
``` 
./manage.py migrate
```

and then install the system crontab
```
crontab scripts/crontab.txt
```

... and your system is installed.  Once enough `Price` objects are stored in the database, you'll be able to begin training your NN / classifiers. (see _Administration_ above ^^)

## Roadmap

### r&d

* [ ] look into three fold cross validation
* [ ] import sentiment analysis
* [ ] look into arbitrage opportunities between exchanges
* [ ] look into classifier on buy or sell, as opposed to neural network. eventually that gets me to buy/sell/hold.
bredth
* [ ] automate the process of selecting strategies for a given market.  
* [ ] expand trader into other markets w. high volume
* [ ] research linear regression -- Heimir says "Your problem sounds like a classical Linear Regression problem"
* [ ] map temporal or spatial nature of the data dependencies (based upon jeff's email) ?
* [ ] test adding bid/ask spread data to input
* [ ] test adding volume data to input
* [ ] test adding RSI / MACD, other indicators to data

### operational

* [ ] make trade bot consider balances (and portfolio distribution) before deciding trade amount
* [X] manually optimmize which NNs parameters are at play
* [X] manually optimize "Algo vs Reality" chart (and subsequent trade decision maker in trade.py)
* [ ] optimize trade amounts

### bugs
* [ ] why doesnt NN recommend buy nearly as much as sell?
    - maybe because NN only contains last 1000 data points (1/3 day).  if only selling happened during taht time, nn will bias towards selling.  duh!
    - notes 2/27 seems like its only recommending buying now.  seems to change its mind every 12 hours http://bits.owocki.com/0w121V3C3j1j/Image%202016-02-27%20at%2010.28.21%20AM.png
* [ ] why are buys 10x the size of sells?
    - debug logging added to determien that
* [ ] can't dump backup.  this severly impacts my ability to local dev

### minor bugs
* [X] spotted once: `django.db.utils.DatabaseError: SSL SYSCALL error: EOF detected` (KO: the system was running out of memory.  solved by adding swap space)

###today 2/27

* [X] What would a major pivot to classifiers mean practically?
    1. [X] enumerate problem space to find successful classifiers
    2. [X] enumerate settings of each classifier type to find even *more* successful ones
    3. [X] abstract parts of NN enumeration into shared mixin or super class?
    4. [X] abstract parts of trading signals into shared mixin or super class?
    5. profit
* [X] fix restore of db
* [X] what if trader only acted upon a timeframe it was traded upon.
    collapse trade timerange into 'granularity'.
    perform action then reverse action granularity minutes later
    probably would have to raise the bar for profit targets so could beat fees

### today march 1

* [X] refactor trading script to take either a NN or classifier
    * perform action then reverse action granularity minutes later
    * [X] trade both BTC_ETH and USDT_BTC
    * [X] each trade script acts on ONE nn or classifier, not consensus of several

###today march 2

* [ ] `/profit` analytics tools can analyze > 1 coin
* [ ] `/optimize` analytics tools can analyze > 1 coin
* [ ] `/optimize` analytics tools can classifier performance
* [X] can i connect a trade back to a classifier?  can i connect a trade to it's profit/loss?
    * maybe if i schedule a job (granularity) minutes out, i can wrap up / whether this trade was a profit or loss.

### march 3 
* [X] perform action then reverse action granularity minutes later
* [x] can i connect a trade back to a classifier?  
* [X] can i connect a trade to it's profit/loss?
    * [X] maybe if i schedule a job (granularity) minutes out
    * [X] record whether original trade was a profit or loss.


<!-- Google Analytics --> 
<img src='https://ga-beacon.appspot.com/UA-1014419-15/owocki/pytrader' style='width:1px; height:1px;' >


