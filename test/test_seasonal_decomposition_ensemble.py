import json
import time

from mock import Mock
from random import shuffle
from rpy2 import robjects
from sure import expect

from lib.modules import base_task, helper
from lib.modules.models import TimeSeriesTuple
from lib.plugins import seasonal_decomposition_ensemble

from fixtures.config import services, analyzer


class TestSeasonalDecompositionEnsemble(object):
    def __init__(self):
        self.config = services['SeasonalDecompositionEnsemble']['worker_options']

    def setUp(self):
        base_task.sink = Mock()
        seasonal_decomposition_ensemble.eval_tukey = Mock(return_value={'flag': 1.0})
        seasonal_decomposition_ensemble.eval_quantile = Mock(return_value={'flag': 0.0})
        seasonal_decomposition_ensemble.time = Mock(return_value=1000)
        # mock r stl package and output
        seasonal_decomposition_ensemble.robjects.r.ts = Mock()
        seasonal_decomposition_ensemble.robjects.r.stl = Mock(return_value=[[[1, 7, 0.1], [2, 7, -0.1], [3, 6, 0.1]]])

        self.options = {
            'service': self.config.keys()[0],
            'params': self.config.values()[0]
        }

        self.test_seasonal_decomposition_ensemble = seasonal_decomposition_ensemble.SeasonalDecompositionEnsemble(
            config=analyzer, logger=None, options=self.options)
        self.test_seasonal_decomposition_ensemble.logger = Mock()

    def tearDown(self):
        self.test_seasonal_decomposition_ensemble = None
        seasonal_decomposition_ensemble.eval_tukey = helper.eval_tukey
        seasonal_decomposition_ensemble.eval_quantile = helper.eval_quantile
        seasonal_decomposition_ensemble.time = time
        seasonal_decomposition_ensemble.robjects.r.ts = robjects.r.ts
        seasonal_decomposition_ensemble.robjects.r.stl = robjects.r.stl

    def stub_read_metric_sink_tdigest(self, key):
        return [json.dumps([[-10, 1], [0, 1], [10, 1]])]

    def stub_read_metric_sink_valid(self, option):
        vals = range(0, 8)
        shuffle(vals)
        for i in vals:
            yield TimeSeriesTuple(name='cpu', timestamp=1000 - i, value=10)

    def stub_read_metric_sink_incomplete(self, option):
        vals = range(0, 8)
        vals.remove(2)
        shuffle(vals)
        for i in vals:
            yield TimeSeriesTuple(name='cpu', timestamp=1000 - i, value=10)

    def stub_read_metric_sink_stale(self, option):
        for i in [2, 0, 1]:
            yield TimeSeriesTuple(name='cpu', timestamp=1000 - 30 - i, value=10)

    def stub_read_metric_sink_missing(self, option):
        vals = range(0, 6)
        shuffle(vals)
        for i in vals:
            yield TimeSeriesTuple(name='cpu', timestamp=1000 - i, value=10)

    def stub_read_metric_sink_invalid(self, option):
        yield None

    def stub_read_data(self, metric):
        if metric == 'service1.out':
            return [TimeSeriesTuple(name='cpu', timestamp=10, value=10),
                    TimeSeriesTuple(name='cpu', timestamp=20, value=10),
                    TimeSeriesTuple(name='cpu', timestamp=30, value=10)]
        elif metric == 'service2.in':
            return [TimeSeriesTuple(name='cpu', timestamp=10, value=20),
                    TimeSeriesTuple(name='cpu', timestamp=20, value=20),
                    TimeSeriesTuple(name='cpu', timestamp=30, value=20)]

    def test_read_tdigest(self):
        self.test_seasonal_decomposition_ensemble.metric_sink.read = self.stub_read_metric_sink_tdigest
        for error_type in ['norm', 'abs']:
            self.test_seasonal_decomposition_ensemble._read_tdigest(error_type)
            exp_tdigest = '[[-10, 1], [0, 1], [10, 1]]'
            expect(self.test_seasonal_decomposition_ensemble.tdigests[error_type].serialize()).to.be.equal(exp_tdigest)

    def test_read_for_valid_data(self):
        self.test_seasonal_decomposition_ensemble._read_tdigest = Mock()
        # for data points in time
        self.test_seasonal_decomposition_ensemble.metric_sink.read = self.stub_read_metric_sink_valid
        data = self.test_seasonal_decomposition_ensemble.read()
        expect(data).to.be.equal([TimeSeriesTuple(name='cpu', timestamp=1000 - 6, value=10),
                                  TimeSeriesTuple(name='cpu', timestamp=1000 - 5, value=10),
                                  TimeSeriesTuple(name='cpu', timestamp=1000 - 4, value=10),
                                  TimeSeriesTuple(name='cpu', timestamp=1000 - 3, value=10),
                                  TimeSeriesTuple(name='cpu', timestamp=1000 - 2, value=10),
                                  TimeSeriesTuple(name='cpu', timestamp=1000 - 1, value=10)])

    def test_read_for_incomplete_data(self):
        self.test_seasonal_decomposition_ensemble._read_tdigest = Mock()
        # for incomplete data points
        self.test_seasonal_decomposition_ensemble.metric_sink.read = self.stub_read_metric_sink_incomplete
        data = self.test_seasonal_decomposition_ensemble.read()
        expect(data).to.be.equal([TimeSeriesTuple(name='cpu', timestamp=1000 - 6, value=10),
                                  TimeSeriesTuple(name='cpu', timestamp=1000 - 5, value=10),
                                  TimeSeriesTuple(name='cpu', timestamp=1000 - 4, value=10),
                                  TimeSeriesTuple(name='cpu', timestamp=1000 - 3, value=10),
                                  TimeSeriesTuple(name='cpu', timestamp=1000 - 2, value=False),
                                  TimeSeriesTuple(name='cpu', timestamp=1000 - 1, value=10)])

    def test_read_for_stale_data(self):
        self.test_seasonal_decomposition_ensemble._read_tdigest = Mock()
        # for incomplete data points
        self.test_seasonal_decomposition_ensemble.metric_sink.read = self.stub_read_metric_sink_stale
        data = self.test_seasonal_decomposition_ensemble.read()
        expect(data).to.be.equal(None)

    def test_read_for_too_few_data(self):
        self.test_seasonal_decomposition_ensemble._read_tdigest = Mock()
        # for incomplete data points
        self.test_seasonal_decomposition_ensemble.metric_sink.read = self.stub_read_metric_sink_missing
        data = self.test_seasonal_decomposition_ensemble.read()
        expect(data).to.be.equal(None)

    def test_read_for_no_data(self):
        self.test_seasonal_decomposition_ensemble._read_tdigest = Mock()
        # for incomplete data points
        self.test_seasonal_decomposition_ensemble.metric_sink.read = self.stub_read_metric_sink_invalid
        data = self.test_seasonal_decomposition_ensemble.read()
        expect(data).to.be.equal(None)

    def test_process_for_invalid_input(self):
        states = self.test_seasonal_decomposition_ensemble.process(None)
        expect(states).to.be.equal((0.0, 0.0, 0.0, 0.0, 0.0, 0.0, {'overall': {'flag': -1.0}}))

    def test_process_for_valid_pos_input(self):
        data = [TimeSeriesTuple('service1', 100, 8.1),
                TimeSeriesTuple('service1', 110, 9.1),
                TimeSeriesTuple('service1', 120, 10)]

        self.options['params']['error_params']['threshold'] = 2
        self.test_seasonal_decomposition_ensemble = seasonal_decomposition_ensemble.SeasonalDecompositionEnsemble(
            config=analyzer, logger=None, options=self.options)

        states = self.test_seasonal_decomposition_ensemble.process(data)
        exp_states = (10.0, 3.0, 6.0, 9.0, 1.0, 0.1, {'abs_quantile': {'flag': 0.0}, 'norm_tukey': {'flag': 1.0}, 'overall': {'consensus': 2.0, 'flag': 1}, 'abs_tukey': {'flag': 1.0}, 'norm_quantile': {'flag': 0.0}})
        expect(states).to.be.equal(exp_states)

    def test_process_for_valid_neg_input(self):
        data = [TimeSeriesTuple('service1', 100, 8.1),
                TimeSeriesTuple('service1', 110, 9.1),
                TimeSeriesTuple('service1', 120, 8)]
        self.options['params']['error_params']['threshold'] = 2
        self.test_seasonal_decomposition_ensemble = seasonal_decomposition_ensemble.SeasonalDecompositionEnsemble(
            config=analyzer, logger=None, options=self.options)

        states = self.test_seasonal_decomposition_ensemble.process(data)
        exp_states = (8.0, 3.0, 6.0, 9.0, -1.0, -1.0 / 9, {'abs_quantile': {'flag': 0.0}, 'norm_tukey': {'flag': 1.0}, 'overall': {'consensus': 2.0, 'flag': 1}, 'abs_tukey': {'flag': 1.0}, 'norm_quantile': {'flag': 0.0}})
        expect(states).to.be.equal(exp_states)

    def test_write(self):
        state = (10.1, 3, 7, 10, 0.1, 0.01, {'overall': {'flag': -1.0}})
        exp_tuples = [TimeSeriesTuple(name='SeasonalDecompositionEnsemble.stle_service1.overall.flag', timestamp=1000, value=-1.0),
                      TimeSeriesTuple(name='SeasonalDecompositionEnsemble.stle_service1.input', timestamp=1000, value=10.1),
                      TimeSeriesTuple(name='SeasonalDecompositionEnsemble.stle_service1.seasonal', timestamp=1000, value=3),
                      TimeSeriesTuple(name='SeasonalDecompositionEnsemble.stle_service1.trend', timestamp=1000, value=7),
                      TimeSeriesTuple(name='SeasonalDecompositionEnsemble.stle_service1.model', timestamp=1000, value=10),
                      TimeSeriesTuple(name='SeasonalDecompositionEnsemble.stle_service1.error', timestamp=1000, value=0.1),
                      TimeSeriesTuple(name='SeasonalDecompositionEnsemble.stle_service1.error_norm', timestamp=1000, value=0.01),
                      ]
        self.test_seasonal_decomposition_ensemble.write(state)
        self.test_seasonal_decomposition_ensemble.output_sink.write.assert_called_with(exp_tuples)
        # for invalid input value
        state = (False, 3, 7, 10, 0.1, 0.01, {'overall': {'flag': -1.0}})
        exp_tuples = [TimeSeriesTuple(name='SeasonalDecompositionEnsemble.stle_service1.overall.flag', timestamp=1000, value=-1.0),
                      TimeSeriesTuple(name='SeasonalDecompositionEnsemble.stle_service1.input', timestamp=1000, value=0.0),
                      TimeSeriesTuple(name='SeasonalDecompositionEnsemble.stle_service1.seasonal', timestamp=1000, value=3),
                      TimeSeriesTuple(name='SeasonalDecompositionEnsemble.stle_service1.trend', timestamp=1000, value=7),
                      TimeSeriesTuple(name='SeasonalDecompositionEnsemble.stle_service1.model', timestamp=1000, value=10),
                      TimeSeriesTuple(name='SeasonalDecompositionEnsemble.stle_service1.error', timestamp=1000, value=0.1),
                      TimeSeriesTuple(name='SeasonalDecompositionEnsemble.stle_service1.error_norm', timestamp=1000, value=0.01),
                      ]
        self.test_seasonal_decomposition_ensemble.write(state)
        self.test_seasonal_decomposition_ensemble.output_sink.write.assert_called_with(exp_tuples)
