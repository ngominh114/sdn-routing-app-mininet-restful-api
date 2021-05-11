class Flow:
    def __init__(self, deviceId, in_port, out_port, dl_dst, timeout):
        self.deviceId = deviceId
        self.timeout = timeout
        self.in_port = in_port
        self.dl_dst = dl_dst
        self.out_port = out_port
class Criteria:
    @staticmethod
    def matchInPort(port):
        return PortCriterion(port)
    @staticmethod
    def matchEthDst(mac):
        return EthCriterion(mac, "ETH_DST")
    @staticmethod
    def matchEthSrc(mac):
        return EthCriterion(mac, "ETH_SRC")
class Instructions:
    @staticmethod
    def output(port):
        return OutputInstruction(port, "OUTPUT")
class EthCriterion:
    def __init__(self, mac, eThType):
        self.mac = mac
        self.type = eThType
class PortCriterion:
    def __init__(self, port):
        self.port = port
        self.type = "IN_PORT"
class OutputInstruction:
    def __init__(self, port, instructionType):
        self.port = port
        self.type = instructionType

class TrafficSelector:
    def __init__(self):
        self.criteria = []
    def matchInPort(self, port):
        self.criteria.append(Criteria.matchInPort(port))
    
    def matchEthSrc(self, mac):
        self.criteria.append(Criteria.matchEthSrc(mac))
    
    def matchEthDst(self, mac):
        self.criteria.append(Criteria.matchEthDst(mac))

class TrafficTreatment:
    def __init__(self):
        self.instructions = []
    def setOutput(self, port):
        self.instructions.append(Instructions.output(port))