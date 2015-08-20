"""
Seasonal Decomposition Ensemble Class
"""
import json
from rpy2 import robjects

from numpy import asarray
from time import time
from tdigest.merge_digest import MergeDigest

from lib.modules.helper import eval_tukey, eval_quantile
from lib.modules.base_task import BaseTask
from lib.modules.models import RedisGeneric
from lib.modules.helper import insert_missing_datapoints
from lib.modules.models import TimeSeriesTuple


class SeasonalDecompositionEnsemble(BaseTask):

    def __init__(self, config, logger, options):
        super(SeasonalDecompositionEnsemble, self).__init__(config, logger, resource={'metric_sink': 'RedisSink',
                                                                                      'output_sink': 'GraphiteSink'})
        self.namespace = 'SeasonalDecompositionEnsemble'
        self.service = options['service']
        self.params = options['params']
        self.error_types = ['norm', 'stl']
        self.tdigests = {}
        self.tdigest_keys = {}
        for error_type in self.error_types:
            self.tdigests[error_type] = MergeDigest()
            self.tdigest_keys[error_type] = 'md_ensemble:%s::%s' % (self.service, error_type)
        self.error_evals = {
            'tukey': eval_tukey,
            'quantile': eval_quantile
        }

    def _read_tdigest(self, error_type):
        tdigest_json = [i for i in self.metric_sink.read(self.tdigest_keys[error_type])]
        if tdigest_json:
            centroids = json.loads(tdigest_json[0])
            [self.tdigests[error_type].add(c[0], c[1]) for c in centroids]

    def read(self):
        metric = self.params['metric']
        period_length = self.params['period_length']
        seasons = self.params['seasons']
        interval = self.params['interval']

        # gather data and assure requirements
        for error_type in self.error_types:
            self._read_tdigest(error_type)

        data = [el for el in self.metric_sink.read(metric)]
        if not data[0]:
            self.logger.error('%s :: No Datapoints. Exiting' % self.service)
            return None

        data = sorted(data, key=lambda tup: tup.timestamp)
        if int(time()) - data[-1].timestamp > 3 * interval:
            self.logger.error('%s :: Datapoints are too old (%d sec). Exiting' % (
                self.service, (int(time()) - data[-1].timestamp)))
            return None

        data = insert_missing_datapoints(data, False, interval)
        if len(data) < period_length * seasons + 1:
            self.logger.error(
                '%s :: Not enough (%d) datapoints. Exiting' % (
                    self.service, len(data)))
            return None

        data = data[-period_length * seasons - 1:-1]

        return data

    def process(self, data):
        error_params = self.params.get('error_params', {})
        if data:
            period_length = self.params['period_length']
            threshold = error_params.get('threshold', 2)
            data = [float(el.value) if el.value else False for el in data]
            input_val = data[-1]
            try:
                r_stl = robjects.r.stl
                r_ts = robjects.r.ts
                r_data_ts = r_ts(data, frequency=period_length)
                r_res = r_stl(r_data_ts, s_window="periodic", robust=True)
                r_res_ts = asarray(r_res[0])
                seasonal = r_res_ts[:, 0][-1]
                trend = r_res_ts[:, 1][-1]
                # _error = r_res_ts[:, 2][-1]
                # due to outtages the trend component can be decreased and
                # and therefore negative model values are possible
                model = seasonal + trend
                model = max(0.01, model)
                _error = input_val - model
            except Exception as e:
                self.logger.error('%s :: STL Call failed: %s. Exiting' % (self.service, e))
                return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, {'overall': {'flag': -1.0}})

            # normalize error
            if _error <= 0:
                error_norm = _error / model
            else:
                error_norm = _error / input_val

            errors = {'norm': error_norm, 'stl': _error}
            states = {'overall': {'flag': 0.0}}
            consensus = 0
            for error_type in self.error_types:
                error = errors[error_type]
                tdigest = self.tdigests[error_type]
                tdigest.add(error, 1.0)
                for method, fnc in self.error_evals.iteritems():
                    combination = '%s_%s' % (error_type, method)
                    state = fnc(error, error_params, tdigest)
                    consensus += state['flag']
                    states[combination] = state
                self.metric_sink.write(
                    [RedisGeneric(self.tdigest_keys[error_type], tdigest.serialize())])

            states['overall']['consensus'] = consensus
            if consensus >= threshold:
                states['overall']['flag'] = 1
            elif consensus <= -threshold:
                states['overall']['flag'] = -1

            return (input_val, seasonal, trend, model, _error, error_norm, states)

        else:
            return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, {'overall': {'flag': -1.0}})

    def write(self, state):
        (input_value, seasonal, trend, model, error, error_norm, states) = state
        prefix = '%s.%s' % (self.namespace, self.service)
        now = int(time())
        tuples = []
        for name, state_dict in states.iteritems():
            for metric, value in state_dict.iteritems():
                tuples.append(TimeSeriesTuple('%s.%s.%s' % (prefix, name, metric), now, value))

        if not input_value:
            input_value = 0.0
        tuples.append(TimeSeriesTuple('%s.%s' % (prefix, 'input'), now, input_value))
        tuples.append(TimeSeriesTuple('%s.%s' % (prefix, 'seasonal'), now, seasonal))
        tuples.append(TimeSeriesTuple('%s.%s' % (prefix, 'trend'), now, trend))
        tuples.append(TimeSeriesTuple('%s.%s' % (prefix, 'model'), now, model))
        tuples.append(TimeSeriesTuple('%s.%s' % (prefix, 'error'), now, error))
        tuples.append(TimeSeriesTuple('%s.%s' % (prefix, 'error_norm'), now, error_norm))

        self.output_sink.write(tuples)

    def run(self):
        data = self.read()
        state = self.process(data)
        self.write(state)
        return True
