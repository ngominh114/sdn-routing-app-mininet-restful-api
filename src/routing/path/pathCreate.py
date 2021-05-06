class PathCreator:
    def __init__(self, graph):
        self.graph = graph
        self.shortestPaths = {}
    def traceShortestLinks(self, currentVertex, parents):
        if (currentVertex == 'NULL'):
            a = []
            return a
        else:
            tracedLinks = self.traceShortestLinks(parents[currentVertex], parents)
            tracedLinks.append(currentVertex)
            return tracedLinks

    def buildPathFromLink(self, tracedDeviceIds):
        size = len(tracedDeviceIds)
        links = []
        for i in range(1,size):
            src = tracedDeviceIds[i-1]
            dst = tracedDeviceIds[i]
            links.append(self.graph.adj[src][dst])
        return links

    def dijkstra(self, src):
        nVertices = self.graph.numberOfDevices
        dist = {}
        added = {}
        for deviceId in self.graph.deviceIds:
            dist[deviceId] = float("inf")
            added[deviceId] = False

        dist[src] = 0.0
        parent = {}
        parent[src] = 'NULL'

        for i in range(nVertices):
            nearestDeviceId = 'NULL'
            shortestDistance = float("inf")
            for deviceId in self.graph.deviceIds:
                if (added[deviceId] == False and dist[deviceId] < shortestDistance):
                    nearestDeviceId = deviceId
                    shortestDistance = dist[deviceId]
            added[nearestDeviceId] = True
            for deviceId in self.graph.deviceIds:
                edgeDistance = self.graph.getCost(nearestDeviceId, deviceId)
                if (edgeDistance > 0 and (shortestDistance + edgeDistance) < dist[deviceId]):
                    parent[deviceId] = nearestDeviceId
                    dist[deviceId] = edgeDistance + shortestDistance
        for dst in self.graph.deviceIds:
            if(src != dst):
                if (len(parent) == 1):
                    path = []
                else: 
                    tracedLink = self.traceShortestLinks(dst, parent)
                    path = self.buildPathFromLink(tracedLink)
                    self.shortestPaths[src][dst] = path

    def updatePath(self):
        deviceIds = self.graph.deviceIds
        for deviceId in deviceIds:
            self.shortestPaths[deviceId] = {}
            self.dijkstra(deviceId)
        
    def createPath(self, src, dst):
        self.updatePath()
        try:
            path = self.shortestPaths[src][dst]
            return path
        except:
            return []

    
    
