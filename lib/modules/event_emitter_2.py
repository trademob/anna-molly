import re
from types import FunctionType, BuiltinFunctionType

from boltons.dictutils import OrderedMultiDict
from twitter.common import log


class EventEmitter2(object):

    def __init__(self):
        """
        """
        self.events = OrderedMultiDict()
        self.on = self.add_listener
        self.off = self.remove_listener
        # TODO: Add listener to remove

    def add_listener(self, event, listener, count=0):
        if (isinstance(listener, FunctionType) or isinstance(listener, BuiltinFunctionType)):
            raise Exception("Invalid Listener: %s" % (str(listener)))
        _event = re.compile(event)
        _listener = {"handler": listener, "calls": 0, "calls_left": count}
        self.events.add(_event, _listener)
        return True

    def emit(self, event, kwargs):
        for pattern, listener in self.events.iteritems(multi=True):
            if pattern.match(event):
                if not listener["calls_left"]:
                    log.debug("Removing Listener: %s on Pattern: %s") % (
                        listener, pattern)
                    self.remove_listener(pattern, listener)
                listener["calls"] += 1
                listener["calls_left"] -= 1
                yield listener["handler"](**kwargs)

    def remove_listener(self, pattern, listener):
        pattern = re.compile(pattern)
        listeners = self.events.getlist(pattern)
        for pattern, _listener in self.events.iteritems(multi=True):
            if _listener['handler'] == listener:
                listener = _listener
                break
        listeners = self.events.getlist(pattern)
        listeners.remove(listener)
        if len(listeners):
            self.events.update({pattern: listeners})
        else:
            self.events._remove(pattern)
        return True

    def on_any(self, listener):
        raise NotImplementedError

    def off_any(self, listener):
        raise NotImplementedError

    def once(self, event, listener):
        self.add_listener(event, listener, left=1)

    def many(self, event, listener, left):
        self.add_listener(event, listener, left)
