import redis
import socket
import cPickle as pickle
from cStringIO import StringIO

from twitter.common.lang import Interface
from twitter.common import log


class Sink(Interface):

    def __init__(self):
        pass

    def connect(self):
        pass

    def write(self):
        pass

    def close(self):
        pass

    def read(self):
        pass


class RedisSink(Sink):

    def __init__(self, config):
        self.config = config
        self.host = config['host']
        self.port = config['port']
        self.db = config['db']
        self.count = 0
        self.pipeline_size = config.get('pipeline_size', 1)
        self.connection = self.connect()

    def connect(self):
        try:
            redis_conn = redis.StrictRedis(host=self.host, port=self.port, db=self.db)
            self.redis_pipeline = redis_conn.pipeline()
            return redis_conn
        except Exception as _e:
            log.error("RedisSink: ConnectionError\n %s %s" % (self.config, str(_e)))

    def write(self, datapoints):
        for datapoint in datapoints:
            self.count += 1
            if datapoint.ttl:
                self.redis_pipeline.setex(
                    datapoint.name,
                    datapoint.ttl,
                    pickle.dumps(datapoint.datapoint)
                )
            else:
                self.redis_pipeline.set(
                    datapoint.name,
                    pickle.dumps(datapoint.datapoint)
                )
                self.redis_pipeline.execute()
            if self.count % self.pipeline_size == 0:
                self.redis_pipeline.execute()

    def read_keys(self, pattern):
        # Note: was switced from SCAN since fetch times were incredibly slow.
        # It is okay to block redis in this case.
        return self.connection.keys(pattern)

    def read(self, pattern):
        for item in self.connection.keys(pattern):
            _item = self.connection.get(item)
            if _item:
                yield pickle.Unpickler(StringIO(_item)).load()

    def iread(self, pattern):
        for item in self.connection.scan_iter(match=pattern):
            _item = self.connection.get(item)
            if _item:
                yield pickle.Unpickler(StringIO(_item)).load()


class GraphiteSink(Sink):

    def __init__(self, config):
        self.config = config
        self.host = config['host']
        self.port = config['port']
        self.prefix = config['prefix']
        self.connection = self.connect()

    def connect(self):
        try:
            sock = socket.socket()
            sock.connect((self.host, self.port))
            return sock
        except Exception as _e:
            log.error("Cannot connect to Graphite Sink with config:%s\n%s" % (self.config, str(_e)))

    def write(self, datapoints):
        for datapoint in datapoints:
            try:
                self.connection.sendall("%s.%s %s %d\n" % (self.prefix, datapoint.name, datapoint.value, datapoint.timestamp))
            except Exception as _e:
                log.error("GraphiteSink: WriteError\n %s \n%s" % (datapoint, str(_e)))
