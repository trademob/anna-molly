import sys
import os.path
from datetime import timedelta

ROOT_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(os.path.join(ROOT_DIR, 'bin'))

import scheduler
from lib.plugins.poll_task import PollTask


class TestScheduler(object):

    # BROKER_URL

    def test_scheduler_broker_url_should_be_set(self):
        scheduler.BROKER_URL.should.equal('someHost')

    # CELERYBEAT_SCHEDULE

    def test_scheduler_celerybeat_schedule_should_be_set(self):
        scheduler.CELERYBEAT_SCHEDULE.should.equal({
            'TukeysFilter': {
                'task': 'lib.app.task_runner',
                'schedule': timedelta(seconds=60),
                'args': (PollTask, {'name': 'TukeysFilter'})
            },
            'SeasonalDecomposition': {
                'task': 'lib.app.task_runner',
                'schedule': timedelta(seconds=300),
                'args': (PollTask, {'name': 'SeasonalDecomposition'})
            },
            'SeasonalDecompositionEnsemble': {
                'task': 'lib.app.task_runner',
                'schedule': timedelta(seconds=180),
                'args': (PollTask, {'name': 'SeasonalDecompositionEnsemble'})
            },
            'FlowDifference': {
                'task': 'lib.app.task_runner',
                'schedule': timedelta(seconds=600),
                'args': (PollTask, {'name': 'FlowDifference'})
            }
        })
