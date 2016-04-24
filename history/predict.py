from history.tools import create_sample_row
from history.models import PredictionTest
import time
from history.tools import print_and_log


def predict_v2(ticker, hidden_layers=15, NUM_MINUTES_BACK=1000, NUM_EPOCHS=1000, granularity_minutes=15,
               datasetinputs=5, learningrate=0.005, bias=False, momentum=0.1, weightdecay=0.0, recurrent=False,
               timedelta_back_in_granularity_increments=0):

    # setup
    print_and_log("(p)starting ticker:{} hidden:{} min:{} epoch:{} gran:{} dsinputs:{} learningrate:{} bias:{} momentum:{} weightdecay:{}\
                  recurrent:{}, timedelta_back_in_granularity_increments:{} ".format(
                  ticker, hidden_layers, NUM_MINUTES_BACK, NUM_EPOCHS, granularity_minutes, datasetinputs,
                  learningrate, bias, momentum, weightdecay, recurrent, timedelta_back_in_granularity_increments))
    pt = PredictionTest()
    pt.type = 'mock'
    pt.symbol = ticker
    pt.datasetinputs = datasetinputs
    pt.hiddenneurons = hidden_layers
    pt.minutes_back = NUM_MINUTES_BACK
    pt.epochs = NUM_EPOCHS
    pt.momentum = momentum
    pt.granularity = granularity_minutes
    pt.bias = bias
    pt.bias_chart = -1 if pt.bias is None else (1 if pt.bias else 0)
    pt.learningrate = learningrate
    pt.weightdecay = weightdecay
    pt.recurrent = recurrent
    pt.recurrent_chart = -1 if pt.recurrent is None else (1 if pt.recurrent else 0)
    pt.timedelta_back_in_granularity_increments = timedelta_back_in_granularity_increments
    all_output = ""
    start_time = int(time.time())

    # get neural network & data
    pt.get_nn()
    sample_data, test_data = pt.get_train_and_test_data()

    # output / testing
    round_to = 2
    num_times_directionally_correct = 0
    num_times = 0
    diffs = []
    profitloss_pct = []
    for i, val in enumerate(test_data):
        try:
            # get NN projection
            sample = create_sample_row(test_data, i, datasetinputs)
            recommend, nn_price, last_sample, projected_change_pct = pt.predict(sample)

            # calculate profitability
            actual_price = test_data[i+datasetinputs]
            diff = nn_price - actual_price
            diff_pct = 100 * diff / actual_price
            directionally_correct = ((actual_price - last_sample) > 0 and (nn_price - last_sample) > 0) \
                or ((actual_price - last_sample) < 0 and (nn_price - last_sample) < 0)
            if recommend != 'HOLD':
                profitloss_pct = profitloss_pct + [abs((actual_price - last_sample) / last_sample) *
                                                   (1 if directionally_correct else -1)]
            if directionally_correct:
                num_times_directionally_correct = num_times_directionally_correct + 1
            num_times = num_times + 1
            diffs.append(diff)
            output = "{}) seq ending in {} => {} (act {}, {}/{} pct off); Recommend: {}; Was Directionally Correct:{}\
                    ".format(i, round(actual_price, round_to), round(nn_price, round_to),
                             round(actual_price, round_to), round(diff, round_to), round(diff_pct, 1),
                             recommend, directionally_correct)
            all_output = all_output + "\n" + output
        except Exception as e:
            if "list index out of range" not in str(e):
                print_and_log("(p)"+str(e))
            pass

    avg_diff = sum([abs(diff[0]) for diff in diffs]) / num_times  # noqa
    pct_correct = 100 * num_times_directionally_correct / num_times
    modeled_profit_loss = sum(profitloss_pct) / len(profitloss_pct)
    output = 'directionally correct {} of {} times.  {}%.  avg diff={}, profit={}'.format(
        num_times_directionally_correct, num_times, round(pct_correct, 0), round(avg_diff, 4),
        round(modeled_profit_loss, 3))
    print_and_log("(p)"+output)
    all_output = all_output + "\n" + output

    end_time = int(time.time())
    pt.time = end_time - start_time
    pt.prediction_size = len(diffs)
    pt.output = all_output
    pt.percent_correct = pct_correct
    pt.avg_diff = avg_diff
    pt.profitloss = modeled_profit_loss
    pt.profitloss_int = int(pt.profitloss * 100)
    pt.save()

    return pt.pk
