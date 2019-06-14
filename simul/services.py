

############################################################################################################
##
## BaseService class definition
##
############################################################################################################


class BaseService(object):
    """
    The class is the service abstraction that is needed to implement the set of middleware and application 
    layer services to simulate. The most interesting feature of the system is the possibility to simulate
    a full stack.
    """

    verbose = False

    def log(self, logged_data):
        """
        makes it possible to log data produced by a service. The string is logged only if the public 
        attribute verbose is set to True. Otherwise the data is not logged.

        :str logged_data: the string to be logged
        """
        if (self.verbose):
            print logged_data

    def handle_message(self, msg):
        """
        This method invoked upon receiving a message by the node receive method.

        :Message msg: the message to be handled
        """
        pass

    def handle_indication(self, msg):
        """
        This method invoked upon receiving a message by the node indication method. The message is generated
        by another service running over the same node.

        :Message msg: the message to be handled
        """
        pass

