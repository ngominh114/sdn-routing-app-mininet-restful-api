# from mininet.net import Mininet
class Graph: 
    def updateGraph(self, data):
        self.adj = {}
        self.switches = []
        if ("switches" in data):
            self.numberOfSwitches = len(data['switches'])
            for switch in data['switches']:
                self.adj[switch['name']] = {}
                self.switches.append(switch['name'])
            if ("links" in data):
                for link in data['links']:
                    srcSw = link['src']['sw']
                    dstSw = link['dst']['sw']
                    if (not srcSw in self.adj):
                        self.adj[srcSw] = {}
                    self.adj[srcSw][dstSw] = link

    def getAdj(self):
        return self.adj

    def getCost(self, src, dst):
        try:
            link = self.adj[src][dst]
            cost = link['delay']
            return cost
        except:
            return -1