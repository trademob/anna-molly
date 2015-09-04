"""
Flow Difference Class
"""
import json

from time import time
from tdigest.merge_digest import MergeDigest

from lib.modules.helper import eval_tukey, eval_quantile
from lib.modules.base_task import BaseTask
from lib.modules.models import RedisGeneric
from lib.modules.models import TimeSeriesTuple


class FlowDifference(BaseTask):

    def __init__(self, config, logger, options):
        super(FlowDifference, self).__init__(config, logger, resource={'metric_sink': 'RedisSink',
                                                                       'output_sink': 'GraphiteSink'})
        self.namespace = 'FlowDifference'
        self.service = options['service']
        self.params = options['params']
        self.error_types = ['norm']
        self.tdigest = MergeDigest()
        self.tdigest_key = 'md_flow:%s' % (self.service)
        self.error_evals = {
            'tukey': eval_tukey,
            'quantile': eval_quantile
        }

    def _read_tdigest(self):
        tdigest_json = [i for i in self.metric_sink.read(self.tdigest_key)]
        if tdigest_json:
            centroids = json.loads(tdigest_json[0])
            [self.tdigest.add(c[0], c[1]) for c in centroids]

    def _read_data(self, metric):
        stale_time = self.params['stale']
        data = [el for el in self.metric_sink.read(metric)]

        if not data or None in data:
            self.logger.error('%s :: No Datapoints for %s. Exiting' % (metric, self.service))
            return None

        data = sorted(data, key=lambda tup: tup.timestamp)
        if int(time()) - data[-1].timestamp > stale_time:
            self.logger.error('%s :: Datapoints are too old (%d sec) for %s. Exiting' % (
                self.service, (int(time()) - data[-1].timestamp), metric))
            return None

        return data

    def process(self):
        in_metric = self.params['in_metric']
        out_metric = self.params['out_metric']
        error_params = self.params.get('error_params', {})
        self._read_tdigest()

        # gather data and assure requirements
        in_data = self._read_data(in_metric)
        out_data = self._read_data(out_metric)

        if in_data and out_data:
            index = -2
            out_val = out_data[index]
            in_val = in_data[index]
            deviation = out_val.value - in_val.value

            self.tdigest.add(deviation, 1.0)
            state = self.error_evals['tukey'](deviation, error_params, self.tdigest)
            self.metric_sink.write(
                [RedisGeneric(self.tdigest_key, self.tdigest.serialize())])
            return (deviation, state)
        else:
            return (0.0, {'flag': -1.0})

    def write(self, state):
        (deviation, states) = state
        prefix = '%s.%s' % (self.namespace, self.service)
        now = int(time())
        tuples = []
        for metric, value in states.iteritems():
            tuples.append(TimeSeriesTuple('%s.%s' % (prefix, metric), now, value))

        tuples.append(TimeSeriesTuple('%s.%s' % (prefix, 'deviation'), now, deviation))
        self.output_sink.write(tuples)

    def run(self):
        state = self.process()
        self.write(state)
        return True
