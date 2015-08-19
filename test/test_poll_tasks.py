from mock import Mock

from fixtures.config import analyzer

from lib.plugins import poll_tasks
from lib.plugins.seasonal_decomposition import SeasonalDecomposition
from lib.plugins.tukeys_filter import TukeysFilter


class TestPollSeasonalDecomposition(object):
    def setUp(self):
        self.app = poll_tasks.app
        poll_tasks.app = Mock()
        self.test_poll_seasonal_decomposition = poll_tasks.PollSeasonalDecomposition(
            config=analyzer, logger=None, options=None)

    def tearDown(self):
        self.test_poll_seasonal_decomposition = None
        poll_tasks.app = self.app

    def test_seasonal_decomposition_should_be_callable(self):
        self.test_poll_seasonal_decomposition.should.be.a(
            poll_tasks.PollSeasonalDecomposition)
        self.test_poll_seasonal_decomposition.should.have.property(
            'plugin').being.equal('SeasonalDecomposition')

    def test_run_valid_input(self):
        self.test_poll_seasonal_decomposition.run()
        poll_tasks.app.task_runner.delay.assert_called_once_with(
            SeasonalDecomposition,
            {'params': {'metric': 'system.loadavg'}, 'service': 'stl_service1'})


class TestPollTukeysFilter(object):
    def setUp(self):
        self.app = poll_tasks.app
        poll_tasks.app = Mock()
        self.test_poll_tukeys_filter = poll_tasks.PollTukeysFilter(
            config=analyzer, logger=None, options=None)

    def tearDown(self):
        self.test_poll_tukeys_filter = None
        poll_tasks.app = self.app

    def test_seasonal_decomposition_should_be_callable(self):
        self.test_poll_tukeys_filter.should.be.a(
            poll_tasks.PollTukeysFilter)
        self.test_poll_tukeys_filter.should.have.property(
            'plugin').being.equal('TukeysFilter')

    def test_run_valid_input(self):
        self.test_poll_tukeys_filter.run()
        poll_tasks.app.task_runner.delay.assert_called_once_with(
            TukeysFilter,
            {'params': {'options': {'quantile_25': 'service.quartil_25'}}, 'service': 'service1'})
