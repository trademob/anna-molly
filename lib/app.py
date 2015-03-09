import sys
import traceback
from celery import Celery
from twitter.common import log

sys.path.append('../')
from modules import config

CONFIG = config.load('/opt/anna-molly/config/analyzer.json')

app = Celery('anna-molly', broker=CONFIG['celery']['broker']['host'])
app.conf.update(
    CELERY_IMPORTS=('celery.task.http'),
    CELERY_RESULT_BACKEND = 'redis',
    CELERY_RESULT_DBURI = CONFIG['celery']['backend']['host'],
    CELERY_RESULT_PERSISTENT = True,
    CELERY_TASK_RESULT_EXPIRES = None
)


@app.task()
def task_runner(plugin, params):
    """
    Run Forrest Run!
    :param plugin: plugin name
    :param params: plugin parameters
    :param dry_run: Default=False
    :return:
    """
    try:
        plugin = plugin(config=CONFIG, logger=log, options=params)
        return plugin.run()
    except:
        traceback.print_exc()
        sys.exit(1)
