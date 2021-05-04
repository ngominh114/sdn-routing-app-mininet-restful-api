# from mininet.net import Mininet
class Node:
    def __init__(self, dst, cost):
        self.dst = dst
        self.cost = cost
class Graph:
    def __init__(self, data):
        self.numberOfDevices = len(data['devices'])
        
    def updateGraph(self, data):
        self.numberOfDevices = len(data['devices'])
        self.adj = {}
        self.deviceIds = []

        for device in data['devices']:
            self.adj[device['id']] = {}
            self.deviceIds.append(device['id'])
        
        for link in data['links']:
            srcId = link['src']['deviceId']
            dstId = link['dst']['deviceId']
            self.adj[srcId][dstId] = link

    def getAdj(self):
        return self.adj

    def getCost(self, src, dst):
        try:
            link = self.adj[src][dst]
            cost = link['delay']
            return cost
        except:
            return -1