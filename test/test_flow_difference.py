import json
import tdigest
from time import time
from mock import Mock
from sure import expect

from lib.modules import base_task
from lib.modules import sink
from lib.modules.models import TimeSeriesTuple
from lib.plugins import flow_difference

from fixtures.config import services, analyzer


class TestFlowDifference(object):
    def __init__(self):
        self.config = services['FlowDifference']['worker_options']

    def setUp(self):
        base_task.sink = Mock()
        flow_difference.tdigest = Mock()
        flow_difference.eval_tukey = Mock(return_value={'flag': 0.0})
        flow_difference.time = Mock(return_value=1000)
        self.options = {
            'service': self.config.keys()[0],
            'params': self.config.values()[0]
        }
        self.test_flow_difference = flow_difference.FlowDifference(
            config=analyzer, logger=None, options=self.options)
        self.test_flow_difference.logger = Mock()

    def tearDown(self):
        base_task.sink = sink
        flow_difference.tdigest = tdigest
        flow_difference.time = time
        self.test_flow_difference = None

    def stub_read_metric_sink_tdigest(self, key):
        return [json.dumps([[-10, 1], [0, 1], [10, 1]])]

    def stub_read_metric_sink_valid(self, option):
        for i in [2, 0, 1]:
            yield TimeSeriesTuple(name='cpu', timestamp=1000 - i, value=10)

    def stub_read_metric_sink_stale(self, option):
        for i in [2, 0, 1]:
            yield TimeSeriesTuple(name='cpu', timestamp=1000 - 20 - i, value=10)

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
        self.test_flow_difference.metric_sink.read = self.stub_read_metric_sink_tdigest
        self.test_flow_difference._read_tdigest()
        exp_tdigest = '[[-10, 1], [0, 1], [10, 1]]'
        expect(self.test_flow_difference.tdigest.serialize()).to.be.equal(exp_tdigest)

    def test_read_data(self):
        # for data points in time
        self.test_flow_difference.metric_sink.read = self.stub_read_metric_sink_valid
        data = self.test_flow_difference._read_data('')
        expect(data).to.be.equal([TimeSeriesTuple(name='cpu', timestamp=1000 - 2, value=10),
                                  TimeSeriesTuple(name='cpu', timestamp=1000 - 1, value=10),
                                  TimeSeriesTuple(name='cpu', timestamp=1000, value=10)])
        # for stale data points
        self.test_flow_difference.metric_sink.read = self.stub_read_metric_sink_stale
        data = self.test_flow_difference._read_data('')
        expect(data).to.be.equal(None)
        # no invalid data
        self.test_flow_difference.metric_sink.read = self.stub_read_metric_sink_invalid
        data = self.test_flow_difference._read_data('')
        expect(data).to.be.equal(None)

    def test_process_invalid_input(self):
        self.test_flow_difference.metric_sink.read = self.stub_read_metric_sink_tdigest
        self.test_flow_difference._read_data = Mock(return_value=None)
        self.test_flow_difference._read_data = Mock(return_value=None)
        states = self.test_flow_difference.process()
        expect(states).to.be.equal((0.0, {'flag': -1.0}))

    def test_process_valid_input(self):
        self.test_flow_difference.tdigest_key = Mock()
        self.test_flow_difference.tdigest = Mock()
        self.test_flow_difference.metric_sink.read = self.stub_read_metric_sink_tdigest
        self.test_flow_difference._read_data = self.stub_read_data
        states = self.test_flow_difference.process()
        expect(states).to.be.equal((10, {'flag': 0}))

    def test_write(self):
        state = (10, {'flag': 0})
        exp_tuples = [TimeSeriesTuple(name='FlowDifference.flow_service1.flag', timestamp=1000, value=0),
                      TimeSeriesTuple(name='FlowDifference.flow_service1.deviation', timestamp=1000, value=10)]
        self.test_flow_difference.write(state)

        self.test_flow_difference.output_sink.write.assert_called_with(exp_tuples)
