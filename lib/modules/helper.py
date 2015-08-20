import bisect
import cPickle as pickle
import sys

from cStringIO import StringIO
from math import exp

from models import TimeSeriesTuple


class SafeUnpickler(object):
    PICKLE_SAFE = {
        'copy_reg': set(['_reconstructor']),
        '__builtin__': set(['object']),
    }

    @classmethod
    def find_class(cls, module, name):
        if module not in cls.PICKLE_SAFE:
            raise pickle.UnpicklingError(
                'Attempting to unpickle unsafe module %s' % module)
        __import__(module)
        mod = sys.modules[module]
        if module not in cls.PICKLE_SAFE[module]:
            raise pickle.UnpicklingError(
                'Attempting to unpickle unsafe class %s' % name)
        return getattr(mod, name)

    @classmethod
    def loads(cls, pickle_string):
        pickle_obj = pickle.Unpickler(StringIO(pickle_string))
        pickle_obj.find_global = cls.find_class
        return pickle_obj.load()


def extract_service_name(name):
    name = name.split('.')[1]
    name = name.split(':')[1]
    return name


def get_closest_datapoint(datapoints, time_now):
    timestamps = [datapoint.timestamp for datapoint in datapoints]
    pos = bisect.bisect_left(timestamps, time_now)
    if pos == 0:
        return datapoints[0]
    if pos == len(timestamps):
        return datapoints[pos - 1]
    if timestamps[pos] - time_now < time_now - timestamps[pos - 1]:
        return datapoints[pos]
    else:
        return datapoints[pos - 1]


def find_step_size(timeseries):
    try:
        step_sizes = [timeseries[i].timestamp - timeseries[i - 1].timestamp
                      for i in range(1, len(timeseries))]
        return max(set(step_sizes), key=step_sizes.count)
    except Exception as _e:
        return None


def insert_missing_datapoints(timeseries, default, step_size):
    metric = timeseries[0].name
    last = timeseries[0].timestamp
    filled_timeseries = []
    for datapoint in timeseries:
        while datapoint.timestamp - last > step_size:
            filled_timeseries.append(
                TimeSeriesTuple(metric, last + step_size, default))
            last += step_size
        filled_timeseries.append(datapoint)
        last = datapoint.timestamp
    return filled_timeseries


def eval_tukey(error, params, tdigest):
    state = {}
    iqr_scaling = params.get('iqr_scaling', 1.5)
    quantile_25 = tdigest.quantile(0.25)
    quantile_75 = tdigest.quantile(0.75)
    iqr = quantile_75 - quantile_25
    lower = quantile_25 - iqr_scaling * iqr
    upper = quantile_75 + iqr_scaling * iqr
    # get minimal thresholds if set
    min_lower = params.get('minimal_lower_threshold', exp(50))
    min_upper = params.get('minimal_upper_threshold', -exp(50))
    flag = 0
    if error > upper and error > min_upper:
        flag = 1
    elif error < lower and error < min_lower:
        flag = -1
    state['flag'] = flag
    state['lower'] = lower
    state['upper'] = upper
    return state


def eval_quantile(error, params, tdigest):
    state = {}
    alpha = params.get('alpha', 0.01)
    lower = tdigest.quantile(alpha / 2)
    upper = tdigest.quantile(1 - alpha / 2)
    # get minimal thresholds if set
    min_lower = params.get('minimal_lower_threshold', exp(50))
    min_upper = params.get('minimal_upper_threshold', -exp(50))
    flag = 0
    if error > upper and error > min_upper:
        flag = 1
    elif error < lower and error < min_lower:
        flag = -1
    state['flag'] = flag
    state['lower'] = lower
    state['upper'] = upper
    state['alpha'] = alpha
    return state
