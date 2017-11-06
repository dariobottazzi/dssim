
class BaseService(object):
    """
    The class is the service abstraction that is needed to implement the set of middleware and application layer services
    to simulate.
    """
    def handle_message(self, receiving_peer, msg):
        """
        This method invoked upon receiving a message by the peer receive method.
        """
        pass