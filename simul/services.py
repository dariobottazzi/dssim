
class BaseService(object):
    """
    The class is the service abstraction that is needed to implement the set of middleware and application layer services
    to simulate.
    """
    def handle_message(self, receiving_node, msg):
        """
        This method invoked upon receiving a message by the node receive method.
        """
        pass