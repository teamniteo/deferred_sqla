class DummyVenusian(object):
    def attach(self, *arg, **kw):
        self.attached = (arg, kw)

class DummyBase(object):
    pass

class DummyEvent(object):
    def listen(self, *arg, **kw):
        self.result = (arg, kw)

