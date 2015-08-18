import sys
import unittest

from mock import Mock

sys.path.append("../")

from fixtures.config import CONFIG

import lib.modules
lib.modules.config = Mock()
lib.modules.config.load.return_value = CONFIG

from lib import app
from lib.plugins import poll_tukeys_filter
from lib.plugins.tukeys_filter import TukeysFilter


class TestPollTukeysFilter(unittest.TestCase):

    def setUp(self):
        poll_tukeys_filter.app = Mock()
        poll_tukeys_filter.config = Mock()
        self.test_poll_tukeys_filter = poll_tukeys_filter.PollTukeysFilter(
            config=CONFIG, logger=None, options=None)

    def tearDown(self):
        self.test_poll_tukeys_filter = None
        poll_tukeys_filter.app = app
        poll_tukeys_filter.config = lib.modules.config

    def test_seasonal_decomposition_should_be_callable(self):
        self.test_poll_tukeys_filter.should.be.a(
            poll_tukeys_filter.PollTukeysFilter)
        self.test_poll_tukeys_filter.should.have.property(
            'plugin').being.equal('TukeysFilter')

    def test_run_valid_input(self):
        poll_tukeys_filter.config.load.return_value = CONFIG
        self.test_poll_tukeys_filter.run()
        poll_tukeys_filter.app.task_runner.delay.assert_called_once_with(TukeysFilter,
                                                                         {'params': {
                                                                             'options': {"quantile_25": "service.quartil_25"}}, 'service': 'service1'}
                                                                         )
