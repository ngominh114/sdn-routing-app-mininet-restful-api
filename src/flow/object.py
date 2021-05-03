class Flow:
    def __init__(self, priority, timeout, isPermanent, deviceId, treatment, selector):
        self.priority, self.timeout, self.isPermanent, self.deviceId, self.treatment, self. selector
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
    def __init__(self, criteria):
        self.criteria = criteria

class TrafficTreatment:
    def __init__(self, instructions):
        self.instructions = instructions