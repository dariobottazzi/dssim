from simul.messages import NetworkMessage, Message
from simul.services import BaseService
from failure_detector import Perfect_Failure_Detector, Availability_Internal_Message


class Monarch_Election (BaseService):

    def __init__(self, env, node):
        self.env = env
        self.node = node
        #self.action = env.process(self.run())
        self.myID = self.node.name
        self.I_am_King = True
        self.verbose = True
        self.kingID = ""

    def am_I_king(self, list_candidates):
        if (len(list_candidates) == 0):
            return ""
        names = []
        for i in list_candidates:
            names.append(i.name)
        names.append(self.myID) # consider all available nodes including self

        return min(names)


    def handle_message(self, msg):
        if isinstance(msg, Availability_Internal_Message):
            self.kingID = self.am_I_king(msg.data)
            if (self.kingID == ""):
                self.log(self.myID + " does non know who the current king is")
            else:
                self.log(self.myID+" thinks that the King is "+self.kingID)





