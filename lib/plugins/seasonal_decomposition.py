"""
Seasonal Decomposition Class
"""
import json
import rpy2.robjects as robjects

from numpy import asarray
from time import time
from tdigest.merge_digest import MergeDigest

from lib.modules.helper import eval_tukey, eval_quantile
from lib.modules.base_task import BaseTask
from lib.modules.models import RedisGeneric
from lib.modules.helper import insert_missing_datapoints
from lib.modules.models import TimeSeriesTuple


class SeasonalDecomposition(BaseTask):

    def __init__(self, config, logger, options):
        super(SeasonalDecomposition, self).__init__(config, logger, resource={'metric_sink': 'RedisSink',
                                                                              'output_sink': 'GraphiteSink'})
        self.namespace = 'SeasonalDecomposition'
        self.service = options['service']
        self.params = options['params']
        self.tdigest_key = 'md:%s' % self.service
        self.tdigest = MergeDigest()
        self.error_eval = {
            'tukey': eval_tukey,
            'quantile': eval_quantile
        }

    def _read_tdigest(self):
        tdigest_json = [i for i in self.metric_sink.read(self.tdigest_key)]
        if tdigest_json:
            centroids = json.loads(tdigest_json[0])
            [self.tdigest.add(c[0], c[1]) for c in centroids]

    def read(self):
        metric = self.params['metric']
        period_length = self.params['period_length']
        seasons = self.params['seasons']
        interval = self.params['interval']

        # gather data and assure requirements
        self._read_tdigest()

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
            error_type = error_params.get('error_type', 'norm')
            error_handling = error_params.get('error_handling', 'tukey')
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
                # error_abs = r_res_ts[:, 2][-1]
                # due to outtages the trend component can be decreased and
                # and therefore negative model values are possible
                model = seasonal + trend
                model = max(0.01, model)
                error_abs = input_val - model
            except Exception as e:
                self.logger.error('%s :: STL Call failed: %s. Exiting' % (self.service, e))
                return (0.0, 0.0, 0.0, 0.0, 0.0, {'flag': -1})

            # normalize error
            if error_abs <= 0:
                error_norm = error_abs / model
            else:
                if input_val:
                    error_norm = error_abs / input_val
                else:
                    error_norm = 1.0

            if error_type == 'norm':
                error = error_norm
            elif error_type == 'abs':
                error = error_abs

            # add error to distribution and evaluate
            self.tdigest.add(error, 1.0)
            state = self.error_eval[error_handling](error, error_params, self.tdigest)
            self.metric_sink.write(
                [RedisGeneric(self.tdigest_key, self.tdigest.serialize())])

            return (input_val, model, seasonal, trend, error, state)

        else:
            return (0.0, 0.0, 0.0, 0.0, 0.0, {'flag': -1})

    def write(self, state):
        (input_value, model, seasonal, trend, error, state) = state
        prefix = '%s.%s' % (self.namespace, self.service)
        now = int(time())
        tuples = []
        for name, value in state.iteritems():
            tuples.append(TimeSeriesTuple('%s.%s' % (prefix, name), now, value))

        if not input_value:
            input_value = 0.0
        tuples.append(TimeSeriesTuple('%s.%s' % (prefix, 'model'), now, model))
        tuples.append(TimeSeriesTuple('%s.%s' % (prefix, 'input'), now, input_value))
        tuples.append(TimeSeriesTuple('%s.%s' % (prefix, 'seasonal'), now, seasonal))
        tuples.append(TimeSeriesTuple('%s.%s' % (prefix, 'trend'), now, trend))
        tuples.append(TimeSeriesTuple('%s.%s' % (prefix, 'error'), now, error))

        self.output_sink.write(tuples)

    def run(self):
        data = self.read()
        state = self.process(data)
        self.write(state)
        return True
