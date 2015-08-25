"""
Poll Scripts
"""
import os

from lib import app
from lib import plugins
from lib.modules import config as config_loader
from lib.modules.base_task import BaseTask


class PollTask(BaseTask):
    def __init__(self, config, logger, options):
        super(PollTask, self).__init__(config, logger, resource={'metric_sink': 'RedisSink'})
        self.plugin_name = options['name']
        self.plugin = getattr(plugins, self.plugin_name)

    def run(self):
        try:
            algo_config = config_loader.load(os.path.join(os.path.dirname(__file__), '../../config/services.json'))
            algo_config = algo_config.get(self.plugin_name)['worker_options']
        except AttributeError:
            return None
        for service, options in algo_config.iteritems():
            if service and options:
                params = {'params': options, 'service': service}
                app.task_runner.delay(self.plugin, params)
        return True
