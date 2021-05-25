from graph import Graph
class PathCreator:
    def __init__(self):
        self.graph = Graph()
        self.shortestPaths = {}
    def traceShortestLinks(self, currentVertex, parents):
        if (currentVertex == 'NULL'):
            a = []
            return a
        else:
            tracedLinks = self.traceShortestLinks(parents[currentVertex], parents)
            tracedLinks.append(currentVertex)
            return tracedLinks

    def buildPathFromLink(self, tracedswitches):
        size = len(tracedswitches)
        links = []
        for i in range(1,size):
            src = tracedswitches[i-1]
            dst = tracedswitches[i]
            links.append(self.graph.adj[src][dst])
        return links

    def dijkstra(self, src):
        nVertices = self.graph.numberOfSwitches
        dist = {}
        added = {}
        for switch in self.graph.switches:
            dist[switch] = float("inf")
            added[switch] = False

        dist[src] = 0.0
        parent = {}
        parent[src] = 'NULL'

        for i in range(nVertices):
            nearestswitch = 'NULL'
            shortestDistance = float("inf")
            for switch in self.graph.switches:
                if (added[switch] == False and dist[switch] < shortestDistance):
                    nearestswitch = switch
                    shortestDistance = dist[switch]
            added[nearestswitch] = True
            for switch in self.graph.switches:
                edgeDistance = self.graph.getCost(nearestswitch, switch)
                if (edgeDistance > 0 and (shortestDistance + edgeDistance) < dist[switch]):
                    parent[switch] = nearestswitch
                    dist[switch] = edgeDistance + shortestDistance
        for dst in self.graph.switches:
            if(src != dst):
                if (len(parent) == 1):
                    path = []
                else: 
                    tracedLink = self.traceShortestLinks(dst, parent)
                    path = self.buildPathFromLink(tracedLink)
                    self.shortestPaths[src][dst] = path

    def updatePath(self):
        switches = self.graph.switches
        for switch in switches:
            self.shortestPaths[switch] = {}
            self.dijkstra(switch)
        
    def createPath(self, src, dst):
        if(src == dst):
            return []
        if src in self.shortestPaths:
            srcPaths = self.shortestPaths[src]
            if dst in srcPaths:
                path = srcPaths[dst]
                return path
        self.updatePath()
        path = self.shortestPaths[src][dst]
        return path

    # def updateCost(newCost):
    