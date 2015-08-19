from mock import Mock

from fixtures.config import analyzer

from lib.plugins import poll_tukeys_filter
from lib.plugins.tukeys_filter import TukeysFilter


class TestPollTukeysFilter(object):
    def setUp(self):
        self.app = poll_tukeys_filter.app
        poll_tukeys_filter.app = Mock()
        self.test_poll_tukeys_filter = poll_tukeys_filter.PollTukeysFilter(
            config=analyzer, logger=None, options=None)

    def tearDown(self):
        self.test_poll_tukeys_filter = None
        poll_tukeys_filter.app = self.app

    def test_seasonal_decomposition_should_be_callable(self):
        self.test_poll_tukeys_filter.should.be.a(
            poll_tukeys_filter.PollTukeysFilter)
        self.test_poll_tukeys_filter.should.have.property(
            'plugin').being.equal('TukeysFilter')

    def test_run_valid_input(self):
        self.test_poll_tukeys_filter.run()
        poll_tukeys_filter.app.task_runner.delay.assert_called_once_with(
            TukeysFilter,
            {'params': {'options': {'quantile_25': 'service.quartil_25'}}, 'service': 'service1'})
