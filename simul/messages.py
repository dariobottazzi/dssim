
class BaseMessage(object):
    """
    The BaseMessage class provides the basic message abstraction and it is needed in order to implement application-specific protocols.
    All basic messages should inherit from the BaseMessage class.
    """

    base_size = 20 # header IP

    def __init__(self, sender, data=None):
        self.sender = sender
        self.data = data

    @property
    def size(self):
        return self.base_size + len(repr(self.data)) # expressed in bytes

    def __repr__(self):
        return '<%s>' % self.__class__.__name__

