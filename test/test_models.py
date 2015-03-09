import sys
import unittest

import sure

sys.path.append('../')
from lib.modules import models


class TestModels(unittest.TestCase):

    def setUp(self):
        self.name = 'cpu'
        self.timestamp = 1234
        self.value = 66.6
        self.ttl = 60
        self.tst = models.TimeSeriesTuple(self.name, self.timestamp, self.value)

    def test_TimeSeriesTuple(self):
        self.tst.should.have.property('name')
        self.tst.should.have.property('value')
        self.tst.should.have.property('timestamp')
        self.tst.name.should.be.a(str)
        self.tst.timestamp.should.be.a(int)
        self.tst.value.should.be.a(float)

    def test_RedisTimestamped(self):
        rt = models.RedisTimeStamped({"ttl": self.ttl}, self.tst)
        rt.should.have.property('datapoint')
        rt.datapoint.should.be.a(models.TimeSeriesTuple)
