# TODO: Async TCP Spout Tests
import pickle
import sys
import unittest

sys.path.append("../")

from mock import Mock
from struct import pack
from sure import expect

from fixtures.config import CONFIG
from lib.modules import spout


class TestInterface(object):

    class TestSpoutInterface(unittest.TestCase):

        def setUp(self):
            self.my_spout = spout.Spout()

        def tearDown(self):
            self.my_spout = None

        def test_spout_properties(self):
            self.my_spout.should.have.property('connect')
            self.my_spout.should.have.property('stream')


# class TestCarbonTcpSpoutInterface(TestInterface.TestSpoutInterface):

#     def stub_read_all(self, length):
#         pickle_package = pickle.dumps(self.data_tuple, 1)
#         size = pack('!I', len(pickle_package))
#         # graphite sends package length in the first 4 bytes and then data
#         if length == 4:
#             return size
#         else:
#             return pickle_package

#     def stub_recv(self, length):
#         # simulates case, that 3 bytes are requested, but only 2 bytes received
#         if length == 3:
#             return_conn_string = self.conn_string[0:2]
#             remaining_conn_string = self.conn_string[2:]
#             self.stub_set_conn_string(remaining_conn_string)
#         # get what you want
#         else:
#             return_conn_string = self.conn_string[0:length]
#             remaining_conn_string = self.conn_string[length:]
#             self.stub_set_conn_string(remaining_conn_string)
#         return return_conn_string

#     def stub_set_conn_string(self, new_value):
#         self.conn_string = new_value

#     def setUp(self):
#         spout.socket.socket.accept = Mock(return_value=(Mock(), None))
#         configuration = CONFIG["SPOUT"]["CarbonTcpSpout"]
#         self.my_spout = spout.CarbonTcpSpout(configuration)
#         self.my_spout.connection = Mock()
#         self.my_spout.connection.recv = self.stub_recv
#         self.conn_string = 'abcde'
#         now = 1234
#         self.data_tuple = ([])
#         self.data_tuple.append(('service1.count.sum', (now, 0.0)))
#         self.data_tuple.append(('service2.count.sum', (now, 10.0)))
#         self.data_tuple.append(('service3.other', (now, 5.0)))

#     def tearDown(self):
#         self.my_spout = None

#     def test_read_all_pickle_for_valid_tcp_data(self):
#         return_value = self.my_spout.read_all_pickle(4)
#         expect(return_value).to.equal('abcd')

#     def test_read_all_pickle_for_invalid_tcp_data(self):
#         return_value = self.my_spout.read_all_pickle(3)
#         expect(return_value).to.equal('abc')

#     def test_receive_pickle(self):
#         self.my_spout.read_all_pickle = self.stub_read_all
#         rec_pickles = self.my_spout.receive_pickle()
#         expect(rec_pickles).to.equal(self.data_tuple)
