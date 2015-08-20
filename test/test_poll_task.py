from mock import Mock

from fixtures.config import analyzer, services

from lib.plugins import poll_task
from lib.plugins import (
    FlowDifference,
    SeasonalDecomposition,
    TukeysFilter,
    SeasonalDecompositionEnsemble
)

PLUGINS = {
    'FlowDifference': FlowDifference,
    'SeasonalDecomposition': SeasonalDecomposition,
    'TukeysFilter': TukeysFilter,
    'SeasonalDecompositionEnsemble': SeasonalDecompositionEnsemble
}


class TestPollTask(object):

    def setUp(self):
        self.app = poll_task.app
        poll_task.app = Mock()

    def tearDown(self):
        poll_task.app = self.app

    def test_poll_task_should_throw_if_plugin_is_invalid(self):
        poll_task.PollTask.when.called_with('SomePlugin',
                                            config=analyzer,
                                            logger=None,
                                            options=None
                                            ).should.throw(AttributeError)

    def test_poll_task_for_each_plugin(self):
            for plugin_name, plugin in PLUGINS.iteritems():
                poll_task.app = Mock()
                self.test_poll_task = poll_task.PollTask(plugin_name, config=analyzer, logger=None, options=None)
                self.test_poll_task.should.have.property('plugin_name').being.equal(plugin_name)
                self.test_poll_task.should.have.property('plugin').being.equal(plugin)
                config = services[plugin_name]['worker_options']
                params = {
                    'service': config.keys()[0],
                    'params': config.values()[0]
                }
                self.test_poll_task.run()
                poll_task.app.task_runner.delay.assert_called_once_with(plugin, params)
