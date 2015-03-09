import sys
import unittest

from mock import Mock

sys.path.append("../")

from fixtures.config import CONFIG

import lib
lib.modules.config = Mock()
lib.modules.config.load.return_value = CONFIG

from lib.plugins import poll_seasonal_decomposition, seasonal_decomposition


class TestPollSeasonalDecomposition(unittest.TestCase):

    def setUp(self):
        poll_seasonal_decomposition.app = Mock()
        self.test_poll_seasonal_decomposition = poll_seasonal_decomposition.PollSeasonalDecomposition(
            config=CONFIG, logger=None, options=None)

    def tearDown(self):
        poll_seasonal_decomposition.app = lib.app
        self.test_poll_seasonal_decomposition = None

    def test_seasonal_decomposition_should_be_callable(self):
        self.test_poll_seasonal_decomposition.should.be.a(
            poll_seasonal_decomposition.PollSeasonalDecomposition)
        self.test_poll_seasonal_decomposition.should.have.property(
            'plugin').being.equal('SeasonalDecomposition')

    def test_run_valid_input(self):
        poll_seasonal_decomposition.app.task_runner.delay = Mock()
        self.algo_config = {'cpu': {'option': 0}}
        self.test_poll_seasonal_decomposition.run()
        poll_seasonal_decomposition.app.task_runner.delay.assert_called_once_with(seasonal_decomposition.SeasonalDecomposition,
                                                                                  {'options': {'option': 0}, 'plugin': 'SeasonalDecomposition', 'service': 'cpu'})

    def test_run_valid_input(self):
        poll_seasonal_decomposition.app.task_runner.delay = Mock()
        self.algo_config = {'cpu': None}
        self.test_poll_seasonal_decomposition.run()
        assert not poll_seasonal_decomposition.app.task_runner.delay.called
