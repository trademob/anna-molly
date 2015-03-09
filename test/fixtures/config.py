CONFIG = {
    "SPOUT": {
        "CarbonTcpSpout": {
            "host": "127.0.0.1",
            "port": 2004,
            "model": "pickle"
        }
    },
    "SINK": {
        "RedisSink": {
            "host": "127.0.0.1",
            "port": 6379,
            "pipeline_size": 100,
            "db": 0
        }
    },
    "metric_sink": {
        "RedisSink": {
            "host": "127.0.0.1",
            "port": 6379,
            "pipeline_size": 100,
            "db": 0
        }
    },
    "output_sink": {
        "GraphiteSink": {
            "host": "127.0.0.1",
            "port": 2003,
            "url": "graphite.foo.com",
            "prefix": "AnnaMolly"
        }
    },
    "celery": {
        "broker": {
            "host": "someHost"
        },
        "backend": {
            "host": "someHost"
        }
    }
}
