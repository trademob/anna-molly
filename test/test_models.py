from lib.modules import models


class TestModels(object):
    def setUp(self):
        self.name = 'cpu'
        self.timestamp = 1234
        self.value = 66.6
        self.ttl = 60
        self.interval = 300
        self.tst = models.TimeSeriesTuple(self.name, self.timestamp, self.value)

    def test_TimeSeriesTuple(self):
        self.tst.should.have.property('name')
        self.tst.should.have.property('value')
        self.tst.should.have.property('timestamp')
        self.tst.name.should.be.a(str)
        self.tst.timestamp.should.be.a(int)
        self.tst.value.should.be.a(float)

    def test_RedisTimestamped(self):
        rt = models.RedisTimeStamped({'ttl': self.ttl}, self.tst)
        rt.should.have.property('datapoint')
        rt.should.have.property('name').equal('cpu:1234')
        rt.should.have.property('ttl').equal(60)
        rt.datapoint.should.be.a(models.TimeSeriesTuple)

    def test_RedisIntervalTimeStamped(self):
        rt = models.RedisIntervalTimeStamped({'ttl': self.ttl, 'interval': self.interval}, self.tst)
        rt.should.have.property('datapoint')
        rt.should.have.property('name').equal('cpu:1200')
        rt.should.have.property('ttl').equal(60)
        rt.datapoint.should.be.a(models.TimeSeriesTuple)

    def test_RedisGeneric(self):
        rt = models.RedisGeneric('generic', self.tst)
        rt.should.have.property('datapoint')
        rt.should.have.property('name').equal('generic')
        rt.datapoint.should.be.a(models.TimeSeriesTuple)
