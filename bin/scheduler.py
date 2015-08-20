"""
The Celery Scheduler
"""

from datetime import timedelta
import os.path
import sys

ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(ROOT)

from lib.modules import config
from lib.plugins.poll_task import PollTask

analyzer_file = os.path.join(os.path.dirname(__file__), '../config/analyzer.json')
analyzer_config = config.load(analyzer_file)
BROKER_URL = analyzer_config['celery']['broker']['host']

# services config
services_file = os.path.join(os.path.dirname(__file__), '../config/services.json')
services_config = config.load(services_file)

CELERYBEAT_SCHEDULE = {}

for algorithm, algo_config in services_config.iteritems():
    scheduler_options = algo_config['scheduler_options']
    CELERYBEAT_SCHEDULE[algorithm] = {
        'task': 'lib.app.task_runner',
        'schedule': timedelta(seconds=scheduler_options['interval_secs']),
        'args': (PollTask, {'plugin_name': scheduler_options['plugin']})
    }
