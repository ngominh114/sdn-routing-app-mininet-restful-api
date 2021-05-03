from data.data import RoutingData
class Graph:
    def __init__(self, data: RoutingData):
        self.numberOfDevices = len(data.devices)
        updateGraph()
    def updateGraph(data: RoutingData):
        self.numberOfDevices = len(data.devices)
        self.adj = {}
        self