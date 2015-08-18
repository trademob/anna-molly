import sys
import unittest
import os.path

from mock import Mock

ROOT_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, 'bin')) # add bin dir to stub collector internals

import collector
from lib.modules.models import TimeSeriesTuple

collector.config = Mock()
collector.config.load.return_value = {
    'router': {
        'blacklist': ['.*_crit.*'],
        'whitelist': {
            'host.ip.*serv1.*cpu.*': [{
              'RedisTimeStamped': { 'ttl': 10 }
}]}}}

# setup the collector once
options = Mock()
collector.setup(options)

class TestCollector(unittest.TestCase):

    def setUp(self):
        self.writer = Mock()
        self.listener = Mock()

    # process

    def test_collector_process_accepts_whitelisted_and_not_blacklisted_metrics(self):
        collector.process(self.writer, TimeSeriesTuple('host.ip.127-0-0-1.serv1.cpu.avg', 1, 1))
        self.writer.write.called.should.be.true

    def test_collector_process_ignores_not_whitelisted_metrics(self):
        collector.process(self.writer, TimeSeriesTuple('host.ip.127-0-0-1.serv2.cpu.avg', 1, 1))
        self.writer.write.called.should.be.false

    def test_collector_process_ignores_whitelisted_but_blacklisted_metrics(self):
        collector.process(self.writer, TimeSeriesTuple('host.ip.127-0-0-1.serv1.cpu_crit.avg', 1, 1))
        self.writer.write.called.should.be.false
