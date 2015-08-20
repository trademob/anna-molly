"""
The Anna-Molly Collector
"""

import re
import sys
import os.path
from functools import partial

from twitter.common import app, log

ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(ROOT)

from lib.modules import spout, config, models, event_emitter_2
from lib.modules import sink


app.add_option("--listener", default="CarbonAsyncTcpSpout",
               help="Select the incoming metric connection interface")
app.add_option("--writer", default="RedisSink",
               help="Select the sink connection interface")
app.add_option("--config", help="Collector Config")

# Globals
EE = event_emitter_2.EventEmitter2()
CONFIG = None
WHITELIST = None
BLACKLIST = None

def setup(options):
    """Load the config file and add listeners for whitelisted metrics.

       :param options: app options
    """
    global WHITELIST, BLACKLIST
    CONFIG = config.load(options.config)
    WHITELIST = CONFIG['router']['whitelist']
    log.debug("Whitelist: %s" % (WHITELIST))
    BLACKLIST = [re.compile(x) for x in CONFIG['router']['blacklist']]
    log.debug("Blacklist: %s" % (BLACKLIST))
    for pattern, mappings in WHITELIST.iteritems():
        for _models in mappings:
            for model, default in _models.iteritems():
                handler = partial(getattr(models, model), defaults=default)
                EE.add_listener(pattern, handler, count=-1)
    return CONFIG

def process(writer, metric):
    """Called for each metric from the listener, rejects all blacklisted metrics and sends transformed data to
       the writer.

       :param writer: The sink where metrics should be written to
       :param metric: TimeSeriesTuple from the listener
    """
    # reject blacklisted metrics
    for pattern in BLACKLIST:
        if pattern.search(metric.name):
            return
    # send whitelisted metrics to the writer
    for m in EE.emit(metric.name, {"datapoint": metric}):
        writer.write([m])


def main(args, options):
    config = setup(options)
    try:
        writer = config['writer'][options.writer]
        log.debug("Connecting to %s writer @ %s" % (options.writer, writer))
        writer = getattr(sink, options.writer)(writer)
    except AttributeError:
        log.error("Could not find metricstore connector interface %s" % (options.writer))
    try:
        listener_config = config['listener'][options.listener]
        listener = getattr(spout, options.listener)(listener_config, partial(process, writer))
        log.debug("Connecting to %s listener @ %s" % (options.listener, listener))
        listener.connect()
    except AttributeError:
        log.error("Could not find connector interface %s" % (options.listener))

app.main()
