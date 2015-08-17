import sys
from datetime import timedelta

sys.path.append('../')

from lib.modules import config
from lib.plugins.poll_tukeys_filter import PollTukeysFilter
from lib.plugins.poll_seasonal_decomposition import PollSeasonalDecomposition


configfile = '/opt/anna-molly/config/analyzer.json'
CONFIG = config.load(configfile)
BROKER_URL = CONFIG['celery']['broker']['host']

CELERYBEAT_SCHEDULE = {
    '1': {
        'task': 'app.task_runner',
        'schedule': timedelta(seconds=30),
        'args': (PollTukeysFilter, {})
    }
}
