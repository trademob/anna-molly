import sink


class BaseTask(object):
    """
    """
    def __init__(self, config, logger, resource={}):
        self.config = config
        self.logger = logger
        self.resource = resource
        self._metric_sink = None
        self._output_sink = None
        self.metric_sink = self.resource.get('metric_sink', None)
        self.output_sink = self.resource.get('output_sink', None)

    @property
    def metric_sink(self):
        return self._metric_sink

    @metric_sink.setter
    def metric_sink(self, value):
        if value:
            config = self.config['metric_sink'][value]
            self._metric_sink = getattr(sink, value)(config)
        else:
            self._metric_sink = None

    @property
    def output_sink(self):
        return self._output_sink

    @output_sink.setter
    def output_sink(self, value):
        if value:
            config = self.config['output_sink'][value]
            self._output_sink = getattr(sink, value)(config)
        else:
            self._output_sink = None

    def run(self):
        raise NotImplementedError
