import redis
import cPickle as pickle

from mock import Mock
from sure import expect

from fixtures.config import sink as sink_config
from lib.modules.models import TimeSeriesTuple, RedisTimeStamped
from lib.modules import sink


class TestInterface(object):

    class TestSinkInterface(object):
        def setUp(self):
            self.my_sink = sink.Sink()

        def tearDown(self):
            self.my_sink = None

        def test_sink_properties(self):
            self.my_sink.should.have.property('connect')
            self.my_sink.should.have.property('write')
            self.my_sink.should.have.property('close')
            self.my_sink.should.have.property('read')

        def test_sink_write(self):
            self.my_sink.connect.when.called_with().should.throw(
                NotImplementedError)


class TestRedisSinkInterface(TestInterface.TestSinkInterface):
    def setUp(self):
        sink.redis = Mock()
        self.configuration = sink_config['RedisSink']
        self.my_sink = sink.RedisSink(self.configuration)
        self.redis_pipeline_list = []

    def tearDown(self):
        sink.redis = redis
        self.configuration = None
        self.my_sink = None
        self.redis_pipeline_list = None
        self.my_sink = None

    def test_sink_properties(self):
        self.my_sink.should.have.property('host')
        self.my_sink.should.have.property('port')
        self.my_sink.should.have.property('pipeline_size')
        self.my_sink.should.have.property('connection')

    def stub_setex(self, metric_name, ttl, metric):
        self.redis_pipeline_list.append((metric_name, ttl, metric))

    def stub_execute(self):
        self.redis_pipeline_list = []

    def test_sink_write(self):
        self.my_sink.redis_pipeline.setex = self.stub_setex
        self.my_sink.redis_pipeline.execute = self.stub_execute
        data_tuple = TimeSeriesTuple('service', 60, 1.0)
        for nr_elements_to_insert in [0, 20]:
            redis_value = [
                RedisTimeStamped({'ttl': 60}, data_tuple)] * nr_elements_to_insert
            self.my_sink.write(redis_value)
            expected_pipeline = [('service:60', 60, (pickle.dumps(TimeSeriesTuple(
                'service', 60, 1.0))))] * (nr_elements_to_insert % self.configuration['pipeline_size'])
            expect(self.redis_pipeline_list).to.equal(expected_pipeline)

    def test_sink_read_keys(self):
        keys = ['service1', 'service2', 'service3',
                'service4', 'service5', 'service6']
        self.my_sink.connection.keys.return_value = keys
        expect(self.my_sink.read_keys(None)).to.equal(keys)

    def test_sink_read_should_return_RedisTimeStamped_models(self):
        data = {}
        keys = ['service1', 'service2', 'service3',
                'service4', 'service5', 'service6']
        self.my_sink.connection.keys.return_value = keys

        for i in range(1, 7):
            service_name = 'service%s' % (i)
            data[service_name] = RedisTimeStamped(
                {'ttl': 120}, TimeSeriesTuple(service_name, 60, 1.0))

        data['service4'] = None

        def stub_get(key):
            item = data.get(key)
            if item:
                return pickle.dumps(item)

        self.my_sink.connection.get = stub_get
        count = 0
        for item in self.my_sink.read(None):
            expect(item).to.be.a(RedisTimeStamped)
            count += 1
        expect(count).to.equal(5)

    def test_sink_iread_should_return_RedisTimeStamped_models(self):
        data = {}
        keys = ['service1', 'service2', 'service3',
                'service4', 'service5', 'service6']
        self.my_sink.connection.scan_iter.return_value = (i for i in keys)
        for i in range(1, 7):
            service_name = 'service%s' % (i)
            data[service_name] = RedisTimeStamped(
                {'ttl': 120}, TimeSeriesTuple(service_name, 60, 1.0))

        data['service4'] = None

        def stub_get(key):
            item = data.get(key)
            if item:
                return pickle.dumps(item)

        count = 0
        self.my_sink.connection.get = stub_get
        for item in self.my_sink.iread(None):
            expect(item).to.be.a(RedisTimeStamped)
            count += 1
        expect(count).to.equal(5)
