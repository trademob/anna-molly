from collections import namedtuple


class TimeSeriesTuple(namedtuple('TimeSeriesTuple', 'name timestamp value')):

    __slots__ = ()

    def __str__(self):
        return "TimeSeriesTuple: name=%s timestamp=%d value=%f" % (
            str(self.name),
            int(self.timestamp),
            float(self.value)
        )


class RedisTimeStamped(object):

    def __init__(self, defaults, datapoint):
        self.ttl = defaults["ttl"]
        self.datapoint = datapoint
        self.name = self.get_name()

    def __str__(self):
        return "%s with TTL: %s" % (self.datapoint, self.ttl)

    def get_name(self):
        return "%s:%d" % (self.datapoint.name, self.datapoint.timestamp)


class RedisGeneric(object):
    def __init__(self, name, datapoint, ttl=None):
        self.datapoint = datapoint
        self.ttl = ttl
        self.name = name
