import sys
import unittest

from mock import Mock

sys.path.append("../")

from fixtures.config import CONFIG

import lib
lib.modules.config = Mock()
lib.modules.config.load.return_value = CONFIG

from lib import app
from lib.plugins import poll_tukeys_filter, tukeys_filter


class TestPollTukeysFilter(unittest.TestCase):

    def setUp(self):
        poll_tukeys_filter.app = Mock()
        self.test_poll_tukeys_filter = poll_tukeys_filter.PollTukeysFilter(
            config=CONFIG, logger=None, options=None)

    def tearDown(self):
        poll_tukeys_filter.app = app
        self.test_poll_tukeys_filter = None

    def test_seasonal_decomposition_should_be_callable(self):
        self.test_poll_tukeys_filter.should.be.a(
            poll_tukeys_filter.PollTukeysFilter)
        self.test_poll_tukeys_filter.should.have.property(
            'plugin').being.equal('TukeysFilter')

    def test_run_valid_input(self):
        #poll_tukeys_filter.app.task_runner.delay = Mock()
        self.algo_config = {'cpu': {'option': 0}}
        self.test_poll_tukeys_filter.run()
        poll_tukeys_filter.app.task_runner.delay.assert_called_once_with(tukeys_filter.TukeysFilter,
                                                                         {'options': {'option': 0}, 'plugin': 'TukeysFilter', 'service': 'cpu'})

    def test_run_invalid_input(self):
        poll_tukeys_filter.app.task_runner.delay = Mock()
        self.algo_config = {'cpu': None}
        self.test_poll_tukeys_filter.run()
        assert not poll_tukeys_filter.app.task_runner.delay.called
