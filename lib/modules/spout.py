import signal
import struct

import pyuv
from twitter.common.lang import Interface
from twitter.common import log

from helper import SafeUnpickler
from models import TimeSeriesTuple


class Spout(Interface):
    """
    Spouts are data source interfaces primarily used by the
    Collector Daemon to recieve the data from a source such
    as StatsD or Carbon.
    """

    def __init__(self):
        pass

    def connect(self):
        """
        Connects to data source.
        """
        raise NotImplementedError

    def stream(self):
        """
        Yields timeseries data as TimeSeriesTuples
        """
        raise NotImplementedError


class CarbonAsyncTcpSpout(Spout):
    """
    PyUV based Int32Pickle metric reciever.
    Recieves data, unpickles it and invokes callback for
    each timeseries datapoint as TimeSeriesTuple
    """

    def __init__(self, config, callback):
        """
        :param config: {"CarbonHost": "127.0.0.1", "CarbonPort": 2014}
        :param callback: Callback for each datapoint recieved
        """
        self.buf = None
        self.host = config['host']
        self.port = config['port']
        self.callback = callback
        self.clients = []
        self.loop = pyuv.Loop.default_loop()
        self.server = pyuv.TCP(self.loop)
        self.signal_handler = pyuv.Signal(self.loop)

    def _signal_cb(self, handle, signum):
        """
        .. warning::Internal method.
        Disconnect and Remove client when data recieved is None.
        """
        [client.close() for client in self.clients]
        self.signal_handler.close()
        self.server.close()

    def _on_connection(self, server, error):
        """
        .. warning::Internal method.
        Connect to client on request
        """
        client = pyuv.TCP(self.server.loop)
        self.server.accept(client)
        self.clients.append(client)
        client.start_read(self._stream)

    def _unpickle(self, infile):
        """
        .. warning::Internal method.
        Unpickle and yield recieved payload
        """
        try:
            bunch = SafeUnpickler.loads(infile)
            yield bunch
        except Exception as _e:
            log.error("UnpicklingError: %s" % (str(_e)))

    def _stream(self, client, data, error):
        """
        .. warning::Internal method.
        Implements Int32StringReciever
        .. note:: Callbacks
            on data: self.callback
            on None: self._signal_cb
        """
        if error:
            log.error("%s" % (error))
        if data is None:
            log.debug("Closing Client %s" % (client))
            client.close()
            self.clients.remove(client)
            return
        if self.buf:
            data = self.buf + data
            self.buf = None
        # Compute Size
        size = data[0:4]
        size = struct.unpack('!I', size)[0]
        log.debug("Read Size: %s\t Received Size: %s" % (size, len(data)))
        # All okay. Read == Received. => Pickel in one packet.
        if size == (len(data) - 4):
            _data = data[4:]
        # Read < Received. => multiple pickles in packet
        elif size < (len(data) - 4):
            # Get one pickle
            _data = data[4:size + 5]
            # Stream rest again. Repeat
            self._stream(None, data[size + 4:], None)
        # Read > Recieved. => Pickle in consecutive packets.
        elif size > (len(data) - 4):
            _data = None
            # Buffer Data
            self.buf = data[size + 4:]

        for datapoints in self._unpickle(_data):
            for datapoint in datapoints:
                print datapoint
                self.callback(TimeSeriesTuple(datapoint[0],
                                              datapoint[1][0],
                                              datapoint[1][1]))

    def connect(self):
        """
        Starts the server
        """
        try:
            log.debug("Connecting to %s:%s" % (self.host, self.port))
            self.server.bind((self.host, self.port))
            self.server.listen(self._on_connection)
            self.signal_handler.start(self._signal_cb, signal.SIGINT)
            self.loop.run()
        except Exception as _e:
            log.error("Could not connect to %s:%s %s" %
                      (self.host, self.port, str(_e)))
