<a href="https://gitcoin.co/explorer?q=">
    <img src="https://gitcoin.co/funding/embed?repo=https://github.com/owocki/pytrader">
</a>

# pytrader
[![Build Status](https://travis-ci.org/owocki/pytrader.svg?branch=master)](https://travis-ci.org/owocki/pytrader)

## What

pytrader is a _cryptocurrency trading robot_ that uses _machine learning_ to predict _price movements_ at _confidence intervals_, and sometimes execute _trades_.  It is programmed to work on the [poloniex.com cryptocurrency platform](http://poloniex.com).

###### Prettymuch, this:

> <img src='http://f.cl.ly/items/2m0p373L030F2y0U0I3p/9d7D_f-maxage-0.gif' />


I (<a href="github.com/owocki">@owocki</a>) built this as a side project in January / February 2016, as a practical means of getting some experience with machine learning, quantitative finance, and of course hopefully making some profit `;)`.

--- 

__3/20/2017__ - This project has been put on ice by it's contributors.  Comment here if you would like to see a revival of development => https://github.com/owocki/pytrader/issues/80

__3/26/2016__ - My test portfolio was initialized with a 1 BTC deposit, and after 2 months and 23,413 trades,  exited with 0.955 BTC.  The system paid 2.486 BTC in fees to poloniex.  CALL TO ACTION -- Get this trader to profitability.    [A strategy is being fleshed out here](https://github.com/owocki/pytrader/issues/1).

__3/27/2016__ - Sign up for the pytrader slack channel [here](https://github.com/owocki/pytrader/issues/23).

__4/3/2016__ - New documentation -- [How to trade with pytrader](https://github.com/owocki/pytrader/blob/master/howto_trade.md)

--- 

## How

pytrader uses _pybrain_ and _sklearn_ to make trade ( buy/sell/hold decisions ), and then acts upon them. 

### 1. sklearn classifiers

Supported classifiers are as follows:

```
["Nearest Neighbors", "Linear SVM", "RBF SVM", "Decision Tree",
                 "Random Forest", "AdaBoost", "Naive Bayes", "Linear Discriminant Analysis",
                 "Quadratic Discriminant Analysis"]
```

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

<img src='https://d3vv6lp55qjaqc.cloudfront.net/items/0Q2O3l2J362K1P0Y3F1V/download.png' />

## Administration & Optimization

Administration of this tool is primarily done through the django admin.  

There's a series of graphs in the admin that show trades, and portfolio profitability over time.

<img src='https://camo.githubusercontent.com/8635b3907f6cdff9862bf6212d79297bdceeae69/687474703a2f2f626974732e6f776f636b692e636f6d2f3371324d33753069334c32672f496d616765253230323031362d30332d32362532306174253230392e32322e3233253230414d2e706e67' />

<img src='https://d3vv6lp55qjaqc.cloudfront.net/items/2d3T2m0Z423T3u0D0J1h/Image%202016-03-26%20at%209.21.16%20AM.png' />

... and allow the graphical debugging of trade decisions ... 

<img src='https://d3vv6lp55qjaqc.cloudfront.net/items/1R452H3T35003e2l0r18/Image%202016-03-26%20at%209.30.04%20AM.png?' />

... and allow the tuning of `PredictionTests`  and `ClassifierTests`  ...

<img src='http://bits.owocki.com/0m3e1i0u0e0a/Image%202016-03-26%20at%209.22.55%20AM.png' />

by each of the native pybrain (Prediction Test) and sklearn (ClassiferTests) parameters ..

<img src='https://d3vv6lp55qjaqc.cloudfront.net/items/2b2W2y1Q1U3v2J0Z0o1p/Image%202016-03-26%20at%209.23.37%20AM.png' />

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

The code is not perfect.  This was a pre-product/market-fit side project. Please feel free to open an _Issue_ if you do not understand something.  CALL TO ACTION -- Get this trader to profitability.    [A strategy is being fleshed out here](https://github.com/owocki/pytrader/issues/1).

## Deployment

After you've cloned the repo, you'll want to create a *pypolo/local_settings.py* file with the following information in it:

```
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

API_KEY = "<POLO_API_KEY>"
API_SECRET = "<POLO_SECRET>"

# Additional Django Apps you with to only be enabled in debug mode.
DEBUG_APPS = []

# this defines whether trade.py will actually submit trades to the poloniex API.  setting to `False` is useful for testing
MAKE_TRADES = True

# the following 4 lines are needed only if you want to be alerted of fail cases (when the trader is not running, etc)
ALERT_EMAIL = '<your_email>'
SMTP_USERNAME = '<smtp_user>'
SMTP_HOST = '<smtp_host>'
SMTP_PASSWORD = '<smtp_pass>'

LOG_FILE = '/var/log/django.log'

# Configuration of the number of threads to be used for predictions - Set to CPU cores + 1 if dedicated machine
NUM_THREADS = 5

# only required for pull_twitter.py
# get this info @ https://apps.twitter.com/
TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''
TWITTER_ACCESS_TOKEN_KEY = ''
TWITTER_ACCESS_TOKEN_SECRET = ''


```

install your requirements

``` 
pip install -r requirements.txt
```

set up your database.. here  are some sample DB configs (place in `pypolo/local_settings.py`):


```
#postgres

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'trader',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'trader',
        'PASSWORD': '<pw>',
        'HOST': '127.0.0.1',  # '127.0.0.1',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',  # '5124',                      # Set to empty string for default.
        'ATOMIC_REQUESTS': True,
    },
}

```


```
#sqllite

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

```

run migration commands

``` 
./manage.py syncdb
./manage.py migrate
```

and then install the system crontab
```
crontab scripts/crontab.txt
```

... and your system is installed.  


Once enough `Price` objects are stored in the database, you'll be able to begin training your NN / classifiers. (see example command `./manage.py pull_prices` below or [download a seed database of prices here](https://github.com/owocki/pytrader/issues/2)).

## How do I optimize pytrader's trades?

See the next document, [How to trade with pytrader](https://github.com/owocki/pytrader/blob/master/howto_trade.md).

## Docker dev setup

[Install docker](https://docs.docker.com/engine/installation/) at least version 1.10.3, and [install docker-compose](https://docs.docker.com/compose/install/) at least version 1.6.2.

- initalize your environment:

```
cp docker-compose.yml.example docker-compose.yml
cp docker/env.example docker/env
cp pypolo/local_settings.py.example pypolo/local_settings.py
```

- Add your POLONIEX_API_KEY and POLONIEX_API_SECRET to docker/env (its gitignored, dont worry)
- Set your PYTRADER_LOGIN and PYTRADER_PASSWORD to docker/env.  This will set the login you use to access the site.
- Build Docker image (compiling stuff for scipy and numpy takes time): `docker-compose build` or pull the images from Docker Hub: `docker-compose pull`
- Run the containers: `docker-compose up`
- Seed your db with newest dump from http://repo.snipanet.com:

```
docker exec -it pytrader_web_1 /root/pytrader/scripts/load_newest_data.sh
```

- visit http://localhost:8000/admin and log in with your PYTRADER\_{LOGIN,PASSWORD} credentials.

### Get shell in pytrader container

```
docker exec -it pytrader_web_1 /bin/bash
```

### Postres dumps

Seed dumps are available from http://repo.snipanet.com. Thanks Snipa22!


<!-- Google Analytics -->
<img src='https://ga-beacon.appspot.com/UA-1014419-15/owocki/pytrader' style='width:1px; height:1px;' >


