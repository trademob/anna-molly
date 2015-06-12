import sys
import unittest

from mock import Mock
from sure import expect

sys.path.append("../")

from fixtures.config import CONFIG

import lib.modules.config
lib.modules.config = Mock()
lib.modules.config.load.return_value = CONFIG

import lib.app
lib.app.task_runner = Mock()

from lib.plugins import poll_seasonal_decomposition, seasonal_decomposition


class TestPollSeasonalDecomposition(unittest.TestCase):

    def setUp(self):
        self.test_poll_seasonal_decomposition = poll_seasonal_decomposition.PollSeasonalDecomposition(
            config=CONFIG, logger=None, options=None)

    def tearDown(self):
        self.test_poll_seasonal_decomposition = None

    def test_seasonal_decomposition_should_be_callable(self):
        self.test_poll_seasonal_decomposition.should.be.a(
            poll_seasonal_decomposition.PollSeasonalDecomposition)
        self.test_poll_seasonal_decomposition.should.have.property(
            'plugin').being.equal('SeasonalDecomposition')

    def test_run_valid_input(self):
        lib.modules.config.load.return_value = CONFIG
        self.test_poll_seasonal_decomposition.run()
        lib.app.task_runner.delay.assert_called_once_with(seasonal_decomposition.SeasonalDecomposition, {
            'params': {'options': []}, 'plugin': 'SeasonalDecomposition', 'service': 'service1'})

    def test_run_invalid_input(self):
        lib.modules.config.load.return_value = {}
        self.test_poll_seasonal_decomposition.run()
        assert not lib.app.task_runner.delay.called
