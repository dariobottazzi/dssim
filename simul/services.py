
class BaseService(object):
    """
    The class is the service abstraction that is needed to implement the set of middleware and application layer services
    to simulate.
    """

    verbose = False

    def log(self, str):
        """This method is invoked to log data."""
        if (self.verbose):
            print str

    def handle_message(self, msg):
        """This method invoked upon receiving a message by the node receive method."""
        pass

