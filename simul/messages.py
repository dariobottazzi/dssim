
class Message(object):

    def __init__(self, data=None):
        self.data = data

    @property
    def size(self):
        return len(repr(self.data))

class NetworkMessage(Message):
    """
    The NetworkMessage class provides the basic message abstraction and it is needed in order to implement application-specific protocols.
    All basic messages should inherit from the NetworkMessage class.
    """
    base_size = 20 # header IP

    def __init__(self, sender, data=None):
        super(NetworkMessage, self).__init__(data)
        self.sender = sender
        #self.data = data

    @property
    def size(self):
        return self.base_size + len(repr(self.data)) # expressed in bytes
