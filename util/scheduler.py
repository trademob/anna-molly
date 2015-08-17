import sys
import os
from datetime import timedelta

sys.path.append('../')

from lib.modules import config
from lib.plugins.poll_tukeys_filter import PollTukeysFilter
from lib.plugins.poll_seasonal_decomposition import PollSeasonalDecomposition


configfile = os.path.join(os.path.dirname(__file__), '../config/analyzer.json')
CONFIG = config.load(configfile)
BROKER_URL = CONFIG['celery']['broker']['host']

CELERYBEAT_SCHEDULE = {
    '1': {
        'task': 'app.task_runner',
        'schedule': timedelta(seconds=30),
        'args': (PollTukeysFilter, {})
    }
}
