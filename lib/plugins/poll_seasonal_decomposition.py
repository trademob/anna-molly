"""
Poll Script for Seasonal Decomposition
"""
import sys
sys.path.append('../')

from .. import app
from lib.modules.base_task import BaseTask
from lib.modules import config as config_loader
from seasonal_decomposition import SeasonalDecomposition


class PollSeasonalDecomposition(BaseTask):

    def __init__(self, config, logger, options):
        super(PollSeasonalDecomposition, self).__init__(config, logger, resource={'metric_sink': 'RedisSink'})
        self.plugin = 'SeasonalDecomposition'

    def run(self):
        """
        """
        algo_config = config_loader.load('/opt/anna-molly/config/services.json')
        algo_config = algo_config.get(self.plugin, {None: None})
        for service, options in algo_config.iteritems():
            if service and options:
                option = {'service': service, 'params': options, 'plugin': self.plugin}
                app.task_runner.delay(SeasonalDecomposition, option)
        return True
