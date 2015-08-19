"""
Poll Scripts
"""
import os
import sys

from lib import app
from lib.modules import config as config_loader
from lib.modules.base_task import BaseTask
from tukeys_filter import TukeysFilter
from seasonal_decomposition import SeasonalDecomposition


class PollTukeysFilter(BaseTask):

    def __init__(self, config, logger, options):
        super(PollTukeysFilter, self).__init__(config, logger, resource={'metric_sink': 'RedisSink'})
        self.plugin = 'TukeysFilter'

    def run(self):
        """
        """
        try:
            algo_config = config_loader.load(os.path.join(os.path.dirname(__file__), '../../config/services.json'))
            algo_config = algo_config.get(self.plugin)['worker_options']
        except AttributeError:
            return None
        for service, options in algo_config.iteritems():
            if service and options:
                params = {'params': options, 'service': service}
                app.task_runner.delay(TukeysFilter, params)
        return True


class PollSeasonalDecomposition(BaseTask):

    def __init__(self, config, logger, options):
        super(PollSeasonalDecomposition, self).__init__(config, logger, resource={'metric_sink': 'RedisSink'})
        self.plugin = 'SeasonalDecomposition'

    def run(self):
        """
        """
        try:
            algo_config = config_loader.load(os.path.join(os.path.dirname(__file__), '../../config/services.json'))
            algo_config = algo_config.get(self.plugin)['worker_options']
        except AttributeError:
            return None
        for service, options in algo_config.iteritems():
            if service and options:
                params = {'params': options, 'service': service}
                app.task_runner.delay(SeasonalDecomposition, params)
        return True
