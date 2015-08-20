import re

from sure import expect
from boltons.dictutils import OrderedMultiDict as OMD

from lib.modules.event_emitter_2 import EventEmitter2

def echo():
    pass


class TestEventEmitter2(object):
    def setUp(self):
        self.ee = EventEmitter2()

    def tearDown(self):
        self.ee = None

    def test_ee2_properties(self):
        self.ee.should.have.property('events')
        self.ee.events.should.be.a(OMD)
        self.ee.should.have.property('add_listener')
        self.ee.should.have.property('remove_listener')
        self.ee.should.have.property('on').being.equal(self.ee.add_listener)
        self.ee.should.have.property('off').being.equal(self.ee.remove_listener)
        self.ee.should.have.property('once')

    def test_add_listener_should_add_a_listener_with_call_count(self):
        return_value = self.ee.add_listener('some_reg.X', echo, 100)
        expect(return_value).to.equal(True)
        event_key = re.compile('some_reg.X')
        expect(self.ee.events.keys()).to.equal([event_key])
        expect(self.ee.events[event_key]['handler']).to.equal(echo)
        expect(self.ee.events[event_key]['calls']).to.equal(0)
        expect(self.ee.events[event_key]['calls_left']).to.equal(100)

    def test_remove_listener_should_detach_event_if_listener_count_is_one(self):
        self.ee.add_listener('some_reg.X', echo, 100)
        return_value = self.ee.remove_listener('some_reg.X', echo)
        expect(return_value).to.equal(True)
        expect(self.ee.events).to.be.a(OMD)
        expect(self.ee.events.keys()).to.equal([])
