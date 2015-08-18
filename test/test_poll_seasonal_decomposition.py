import sys
import unittest

from mock import Mock

sys.path.append("../")

from fixtures.config import CONFIG

import lib.modules
lib.modules.config = Mock()
lib.modules.config.load.return_value = CONFIG


from lib import app
from lib.plugins import poll_seasonal_decomposition
from lib.plugins.seasonal_decomposition import SeasonalDecomposition


class TestPollSeasonalDecomposition(unittest.TestCase):

    def setUp(self):
        poll_seasonal_decomposition.app = Mock()
        self.test_poll_seasonal_decomposition = poll_seasonal_decomposition.PollSeasonalDecomposition(
            config=CONFIG, logger=None, options=None)

    def tearDown(self):
        self.test_poll_seasonal_decomposition = None
        poll_seasonal_decomposition.app = app

    def test_seasonal_decomposition_should_be_callable(self):
        self.test_poll_seasonal_decomposition.should.be.a(
            poll_seasonal_decomposition.PollSeasonalDecomposition)
        self.test_poll_seasonal_decomposition.should.have.property(
            'plugin').being.equal('SeasonalDecomposition')

    def test_run_valid_input(self):
        self.test_poll_seasonal_decomposition.run()
        poll_seasonal_decomposition.app.task_runner.delay.assert_called_once_with(SeasonalDecomposition,
                                                                                  {'params': {'metric': 'system.loadavg'}, 'service': 'stl_service1'})
