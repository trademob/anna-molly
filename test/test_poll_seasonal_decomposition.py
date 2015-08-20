from mock import Mock

from fixtures.config import analyzer

from lib.plugins import poll_seasonal_decomposition
from lib.plugins.seasonal_decomposition import SeasonalDecomposition


class TestPollSeasonalDecomposition(object):
    def setUp(self):
        self.app = poll_seasonal_decomposition.app
        poll_seasonal_decomposition.app = Mock()
        self.test_poll_seasonal_decomposition = poll_seasonal_decomposition.PollSeasonalDecomposition(
            config=analyzer, logger=None, options=None)

    def tearDown(self):
        self.test_poll_seasonal_decomposition = None
        poll_seasonal_decomposition.app = self.app

    def test_seasonal_decomposition_should_be_callable(self):
        self.test_poll_seasonal_decomposition.should.be.a(
            poll_seasonal_decomposition.PollSeasonalDecomposition)
        self.test_poll_seasonal_decomposition.should.have.property(
            'plugin').being.equal('SeasonalDecomposition')

    def test_run_valid_input(self):
        self.test_poll_seasonal_decomposition.run()
        poll_seasonal_decomposition.app.task_runner.delay.assert_called_once_with(
            SeasonalDecomposition,
            {'params': {'metric': 'system.loadavg'}, 'service': 'stl_service1'})
