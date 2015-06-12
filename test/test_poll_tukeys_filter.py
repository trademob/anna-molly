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

from lib.plugins import poll_tukeys_filter, tukeys_filter


class TestPollTukeysFilter(unittest.TestCase):

    def setUp(self):
        self.test_poll_tukeys_filter = poll_tukeys_filter.PollTukeysFilter(
            config=CONFIG, logger=None, options=None)

    def tearDown(self):
        self.test_poll_tukeys_filter = None

    def test_seasonal_decomposition_should_be_callable(self):
        self.test_poll_tukeys_filter.should.be.a(
            poll_tukeys_filter.PollTukeysFilter)
        self.test_poll_tukeys_filter.should.have.property(
            'plugin').being.equal('TukeysFilter')

    def test_run_valid_input(self):
        lib.modules.config.load.return_value = CONFIG
        self.test_poll_tukeys_filter.run()
        lib.app.task_runner.delay.assert_called_once_with(tukeys_filter.TukeysFilter, {
            'params': {'options': []}, 'plugin': 'TukeysFilter', 'service': 'service1'})

    def test_run_invalid_input(self):
        lib.modules.config.load.return_value = {}
        self.test_poll_tukeys_filter.run()
        assert not lib.app.task_runner.delay.called
