sink = {
    'RedisSink': {
        'host': '127.0.0.1',
        'port': 6379,
        'pipeline_size': 100,
        'db': 0
    }
}

spout = {
    'CarbonTcpSpout': {
        'host': '127.0.0.1',
        'port': 2004,
        'model': 'pickle'
    }
}

analyzer = {
    'metric_sink': {
        'RedisSink': {
            'host': '127.0.0.1',
            'port': 6379,
            'pipeline_size': 100,
            'db': 0
        }
    },
    'output_sink': {
        'GraphiteSink': {
            'host': '127.0.0.1',
            'port': 2003,
            'url': 'graphite.foo.com',
            'prefix': 'AnnaMolly'
        }
    },
    'celery': {
        'broker': {
            'host': 'someHost'
        },
        'backend': {
            'host': 'someHost'
        }
    },
}

services = {
    'TukeysFilter': {
        'service1': {
            'options': {
                'quantile_25': 'service.quartil_25'
            }
        }
    },
    'SeasonalDecomposition': {
        'stl_service1': {
            'metric': 'system.loadavg'
        }
    }
}

collector = {
    'router': {
        'blacklist': ['.*_crit.*'],
        'whitelist': {
            'host.ip.*serv1.*cpu.*': [{
              'RedisTimeStamped': { 'ttl': 10 }
            }]
        }
    }
}
