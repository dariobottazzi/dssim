

########################################################################################################################
##
## Message class definition
##
########################################################################################################################


class Message(object):
    """The Message class represents a message

     The Message class represent the messages that node exchange during distributed algorithm execution. The Message
     class is the superclass from which all messages inherit their behaviour.

     Attributes
     ----------
     data : obj
        represents the data to be communicated

    """

    def __init__(self, data=None):
        """constructor for the Message class

        The method has one only parameter, i.e. data, representing the message body. Type and content of the data
        parameter depend on what message sender means to message message recipient. It is also possible to send messages
        with void data. This messages can be used for signalling purposes.

        Parameters
        ----------
            data : obj

        """
        self.data = data

    @property
    def size(self):
        """the size property of the message.

        The size of the message is expressed in bytes. This parameter affects the time needed to communicate the
        message.

        """
        return len(repr(self.data))


########################################################################################################################
##
## NetworkMessage class definition
##
########################################################################################################################


class NetworkMessage(Message):
    """The NetworkMessage represent the actual IP message to be communicated.

    The NetworkMessage class inherit its characteristics from the Message abstraction. The main difference between
    Message and NetworkMessage is the actual lenght of the packet. Whereas the size of a Message depends only on the
    size of the data object, the NetworkMessage size adds further 20 Bytes, to keep into account IP packet header size.
    In addition, the message records also the sender of the message.
    """

    __base_size = 20 # header IP

    def __init__(self, sender, data=None):
        """constructor for the NetworkMessage class

        The method has one two parameters, namely sender and  data. The sender represent the sender node, whereas data
        represents the message body. Type and content of the data parameter depend on what message sender means to
        message message recipient. It is also possible to send messages with void data. This messages can be used for
        signalling purposes.

        Parameters
        ----------
            sender: Node
            data  : obj

        """
        super(NetworkMessage, self).__init__(data)
        self.sender = sender

    @property
    def size(self):
        """the size property of the message.

        The size of the message is expressed in bytes. This parameter affects the time needed to communicate the
        message.

        The size of the message includes 20 bytes to keep into account IP header size

        """
        return self.__base_size + len(repr(self.data)) # expressed in bytes
