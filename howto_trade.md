# Trading with pytrader

This document is intended for those who have [successfully deployed the repository onto their own server](https://github.com/owocki/pytrader#deployment), and would like to understand how to optimize towards profit.

## Poloniex Setup

To setup your poloniex account

1. [Sign up](https://www.poloniex.com/signup)
2. Go to `Balances > Deposits & Withdrawals`
3. Scroll to `[BTC] Bitcoin`
4. Get your deposit address.
5. Send BTC to your deposit address. 
    * Note: You will need a way to get BTC.  I use [Coinbase](coinbase.com), but YMMV.
6. Wait until the transaction is confirmed.

To use your poloniex account with pytrader.

1. Navigate to `[wrench] > API Keys` [{screenshot}](http://bits.owocki.com/0D472H0O3108/Image%202016-04-03%20at%201.31.13%20PM.png)
1. Generate an API key that has "enable trading" set to true.
2. Add your APIKey / Secret to your `pypolo/local_settings.py` file:

```
API_KEY = "<POLO_API_KEY>"
API_SECRET = "<POLO_SECRET>"
```

## Concepts: Models

Here is the database model of the repository:

<img src='https://camo.githubusercontent.com/dd089aa7c684700b81a83a4853af965a7ff12511/687474703a2f2f626974732e6f776f636b692e636f6d2f33373368317a326c325633782f646f776e6c6f61642e706e67' />

### Core models

The core models, for optimization, are as follows:

* **ClassifierTest** - a wrapper around *sklearn Classifiers*, that runs a classifier to get a *buy, sell, or hold*, given a set of inputs (right now, a *sample of price sequences*, but in the future could include many other dimensions ) 
* **PredictionTest** - a wrapper around *pybrain Supervised Learning* functionality, that runs a neural network to get a *predicted price*, given a set of inputs (right now, a *sample of price sequences*, but in the future could include many other dimensions ) 

ClassifierTests and PredictionTests both have the following in common:

* take the same input.
* their output is (or can be interpreted as) as a buy/sell/hold.
* they are cheap to create, run, and store in the database (thanks to being django models)

ClassifierTests and PredictionTests differ in that:

* the former predicts a buy/sell/hold, the latter predicts a next price.

## Concepts: The Web UI

For reference, here are the UI views presently in the repo.  They are linked in `/admin`:

1. [Django admin](http://bits.owocki.com/2w0H33103R3f/Image%202016-04-02%20at%2010.51.32%20AM.png)
2. [Portfolio view](http://bits.owocki.com/3z0G123i3i1X/Image%202016-04-02%20at%2010.50.54%20AM.png) - Reperesnts an overview of your portfolio.
3. [Trader optimizer](http://bits.owocki.com/3s1o432E1z2T/Image%202016-04-02%20at%2010.51.45%20AM.png) - Gauges how reliable your trade.py configurations are at reprsenting the market.
4. [NN optimizer](http://bits.owocki.com/06233d3s0414/Image%202016-04-02%20at%2010.52.09%20AM.png) - Helps you pick which `PredictionTest` configurations to trade with.
5. [Classifier optimizer](http://bits.owocki.com/002I3S1Q3G0Q/Image%202016-04-02%20at%2010.52.21%20AM.png) - Helps you pick which `ClassifierTest` configurations to trade with.

## Combining core concepts 

### The search for alpha

In order to find configurations of Classifier/PredictionTests that are correct as often as possible (and wrong as little as possible), I have taken the approach of enumerating through as many possible permutations of configurations of each.  For each configuration, I test against a sample input, and record how often this configuration was correct.

* The [predict_many_sk.py management command](https://github.com/owocki/pytrader/blob/master/history/management/commands/predict_many_sk.py) enumerates through *ClassifierTests*, and outputs a *percent_correct* for each.
* The [predict_many_v2.py management command](https://github.com/owocki/pytrader/blob/master/history/management/commands/predict_many_v2.py) enumerates through *PredictionTests*, and outputs a *percent_correct* for each.

Take a moment to look at the code for each of the above.  I'll wait.

You're back?  Cool -- So you've seen that each management command is basically a series of nested for loops, the sum of all of them is a *brute force enumeration* of each parameter.

NOTE: Both predict_many_sk, and predict_many_v2 are [scheduled to run in the background](https://github.com/owocki/pytrader/blob/master/scripts/crontab.txt).  They can each take several hours to complete.

#### Finding a local maxima

Run both `./manage.py predict_many_sk`, and `./manage.py predict_many_v2`.  Come back after they've completed (a few hours depending upon how powerful your server is).

1. Fire up a web browser, and point it to your local installation.  Check out `admin/nn_charts`) or follow the link from the django admin.
2. You'll see [something like this](http://bits.owocki.com/0W0N1e2B260w/Image%202016-04-03%20at%2011.01.51%20AM.png).
3. Check out the table of contents to the right. Those are all of the parameters to your neural network.
4. Note [the metadata at the top of the control panel](http://bits.owocki.com/191z1O1i2Z1o/Image%202016-04-03%20at%2011.03.03%20AM.png).  Using this, you can see some statistical information about the `percent_correct`ness of your test runs.  You can also change the ticker being viewed, or expand the search parameter for PredictionTests being included in the UI.
5. Check out the graphs in the main part of the control panel.  Thats the distribution of `percent_correct`ness by each parameter.
6. There is a table below each graph.  Try clicking on one of those links. [For example, I'm going to click on datasetinputs](http://bits.owocki.com/220U0Z3Z3443/Image%202016-04-03%20at%2011.05.01%20AM.png).
7. Notice anything different about the metadata stats [at the top of this new page](http://bits.owocki.com/0l2D441l0W3m/Image%202016-04-03%20at%2011.05.32%20AM.png)?  The median `percent_correct`ness has jumped from 52% to 57%!
8. Recursively follow steps 6 -> 7 until 
    1. You have a sample size that's too small to be meaningful.
    2. -- or -- You've reached a `percent_correctness` you are comfortable trading with.

**NOTE** -- The above TODO list is written for `PredictionTest`s, but instructions apply for `ClassifierTest`s also. (Just start at `admin/c_charts` instead of `admin/nn_charts` to tune `ClassifierTests`. )

#### Run more tests

IFF you have a sample size that's too small to be meaningful, you'll want to modify the parameters in the [predict_many_v2.py management command](https://github.com/owocki/pytrader/blob/master/history/management/commands/predict_many_v2.py) to **narrow** your search area to only those parameters.  Re-run, and repeat the steps in "Finding a local maxima", above.

**NOTE** -- The above note is written for `PredictionTest`s, but instructions apply for `ClassifierTest`s also. (Just start at `predict_many_sk.py` instead of `predict_many_v2.py` to tune `ClassifierTests`. )


### Trading

IFF You've reached a `percent_correctness` you are comfortable trading with, it's time to trade!

Open up [trade.py](https://github.com/owocki/pytrader/blob/master/history/management/commands/trade.py) and take a look at [these lines](https://github.com/owocki/pytrader/blob/master/history/management/commands/trade.py#L22-L59).  Do some of those parameters look familiar?  They should, they are parameters you tuned in the `predict_many_*` jobs above.

Replace the default variables in `trade.py` with the parameters that you've found to be successful through your testing in the "Finding a local maxima" section.

Save your file, deploy it to your server, and run `./manage.py trade`.  Congratulations, you are now trading with pytrader!

#### Monitoring your profitability

After you've been trading for a few hours, fire up `admin/optimize` (or click the link in the admin).  You'll see your [trades over time and trade profitability over time](http://bits.owocki.com/1n170Y0f2T0a/Image%202016-04-03%20at%2011.15.30%20AM.png).  

1. Check for any errors in your trades (first 2 graphs).  If you see errors, you may want to check out `admin/history/trade/` (or follow the links in the django admin) to see why your trades are erroring out.  Here is a common one: `{u'error': u'Not enough BTC.'}`
2. There are some other graphs I've used to visually judge whether my trade.py parameters are correctly predicting the market.  TBH, those are a little half baked at the moment, and could use a tune up. [Github Issue](https://github.com/owocki/pytrader/issues/38).

Check out the `admin/profit` page (or click the link in the admin). 

1. In the [top two graphs](http://bits.owocki.com/282p070E2M2x/Image%202016-04-03%20at%2011.20.18%20AM.png), you'll see your balance vs deposited amount over time, and also a breakdown of your balances by currency.
2. You'll also see your realized / unrealized gains in the [bottom table](http://bits.owocki.com/310K201X2H1n/Image%202016-04-03%20at%2011.21.12%20AM.png).
3. [These graphs can be tuned by base currenty](http://bits.owocki.com/440b3a3S380G/Image%202016-04-03%20at%2011.21.46%20AM.png)

#### trade.py 

At a high level, trade.py

1. accepts [predictor_configs](https://github.com/owocki/pytrader/blob/master/history/management/commands/trade.py#L20)
2. [trains NN/classifiers](https://github.com/owocki/pytrader/blob/master/history/management/commands/trade.py#L228) on those configs
3. Runs a [while loop](https://github.com/owocki/pytrader/blob/master/history/management/commands/trade.py#L286) that:
    1. [determines if it's time to make a trade evaluation](https://github.com/owocki/pytrader/blob/master/history/management/commands/trade.py#L292)
    2. [closes any existing open orders, if needed](https://github.com/owocki/pytrader/blob/master/history/management/commands/trade.py#L298)
    3. [runs each predictor](https://github.com/owocki/pytrader/blob/master/history/management/commands/trade.py#L302-L307) in self.predictor_configs, to preduct `recommendations` (an array of buy/sell/hold recommendations)
    4. Determines whether to [act_upon_recommendations](https://github.com/owocki/pytrader/blob/master/history/management/commands/trade.py#L315).
    5. If a buy/sell action is determined to be attempted:
        1. [Determine a price](https://github.com/owocki/pytrader/blob/master/history/management/commands/trade.py#L134-L139)
        2. [Determine a trade amount](https://github.com/owocki/pytrader/blob/master/history/management/commands/trade.py#L142-L145)
        3. [Perform the action](https://github.com/owocki/pytrader/blob/master/history/management/commands/trade.py#L149-L163) and [record the action](https://github.com/owocki/pytrader/blob/master/history/management/commands/trade.py#L166-L178)
        4. [Schedule an opposite trade](https://github.com/owocki/pytrader/blob/master/history/management/commands/trade.py#L183-L198), which will later be executed by [./manage.py scheduled_trades](https://github.com/owocki/pytrader/blob/master/history/management/commands/scheduled_trades.py).
        
## FAQ

### How do I test/trade other currency pairs?

1. Modify the `ticker_options` variable in `predict_many_sk.py` and `predict_many_v2.py`, and follow the instructions in "Finding a local maxima" above.

### What is 'granularity' and why is it important?

Granularity is the size of a chart candlestick.  If 

* `granularity == 1`, the trader will optimize on 1 minute candlesticks.  `trade.py` will trade every `1` minute
* `granularity == 5`, the trader will optimize on 5 minute candlesticks.  `trade.py` will trade every `5` minutes
* `granularity == 120`, the trader will optimize on 120 minute candlesticks.  `trade.py` will trade every `120` minutes
* etc

### Can we trade in simulation mode?

    
You could if you (shameless plug) write some code and submit a PR back to the repo. To test the code, I made a 1 BTC deposit on poloniex and traded with it.  For me, 1 BTC is a negligible amount that was worth not having to manage the abstraction overhead of a simulation mode.

### Are there take profit (TP) and stop loss (SL) settings?

No.

### How many trades can be entered at any given time? 

`len(self.predictor_configs)` over every `self.granularity` minutes.   [see trade.py](https://github.com/owocki/pytrader/blob/master/history/management/commands/trade.py#L25).

### How do we reset the algorithms?

Just 

1. change `predict_many_*.py` to look at new configuration parameters.  
2. -or- change `predictor_configs` in [trade.py](https://github.com/owocki/pytrader/blob/master/history/management/commands/trade.py#L25).

    
    
### Can multiple instruments be traded at the same time? How do we tell pytrader which instruments to trade?

(assuming instrumetns == currency pairs)

Yes, change `symbol` of the NN you'd like to trade with in `predictor_configs` in [trade.py](https://github.com/owocki/pytrader/blob/master/history/management/commands/trade.py#L25).
        
        
### Can pytrader take multiple positions in the same instrument in different directions? How is that managed?

Yes, it can.  Here is an [open issue](https://github.com/owocki/pytrader/issues/39) for tracking the task of managing fees.

### Is there a 'max time in trade' setting after which the position is closed? How to adjust?

Right now trades will be closed after `granularity` minutes.

[This would be easy to tune](https://github.com/owocki/pytrader/blob/master/history/management/commands/trade.py#L183-L198) and I would welcome a PR for this feature.

### How is position sizing determined?

[See this code](https://github.com/owocki/pytrader/blob/master/history/management/commands/trade.py#L86).  TLDR - The `trade.py` script makes an attempt at determining it's `confidence` in a position, and linearly adjusts its position from that.  PRs welcome.

### I noticed we're not running any NN's for USDT_BTC, but are for ETH_BTC. Is there a reason or is that just arbitrary?

Just arbitrary. My interest in trading USDT_BTC as a manual trader happened just as I was writing classifiertests.

### Is there any rhyme or reason to the number of NN's and/or classifier tests run per pair?

This will depend upon your available computational resources and how quickly you want results from the NN/classifiers. As an example, on a small VM with 0.5G of memory, I went through the optimization above 3x, at a cost of ~12 hours of compute per day, before I started trading. Whether that was enough optimization or I was just lucky is a matter of debate at the moment.

### How is the weighting handled and how are they blended?

The weighting is very rudimentary. See [above](https://github.com/owocki/pytrader/blob/owocki/trade_instructions/howto_trade.md#tradepy).

### Why do bad things happen when you try to tune the classifiers (e.g. adjust datasetinput based on simulations)?

This hasn't been implemented yet. You can alter parameters on the NNs, and should be able to adjust classifier type, but I haven't gotten around to adding more customization to classifiertests. We have an open issue [here](https://github.com/owocki/pytrader/issues/43) to track this.

## Reference: Other Important Administration Commands

### Neural Network Backtester

```
./manage.py predict_many_v2
```

### Classifier Backtester

```
./manage.py predict_many_sk
```

### Trade Bot

```
./manage.py trade
```

### Other Administration Commands

These should ideally be scheduled via crontab:

```
./manage.py pull_deposits #checks API for any new deposits
./manage.py pull_balance #records your balance in USD, BTC, native coin.
./manage.py scheduled_trades # executes any _scheduled_ trades
./manage.py pull_prices #pulls price data from exchanges
```
