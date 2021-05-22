import networkx
import random
from mininet.net import Mininet
from mininet.node import RemoteController
class MininetSim():
    def __init__(self):
        self.net = Mininet(topo=None, build=False)
        self.dpid_to_sw = {}
        self.dpid_prefix = "00000000000000"
        self.nodeMapNet = {}
        self.number_of_switch = 0
        self.number_of_host = 0
        self.c_ip = []
    def generate(self, config):
        number_of_controllers = len(config["CONTROLLER_IP"])
        for i in range(number_of_controllers):
            self.c_ip.append(config["CONTROLLER_IP"]["ip_%s"%i])
        filename = config["DIRECTORIES"]["topo"]
        graph = networkx.read_graphml(filename)
        nodes = graph.nodes()
        edges = graph.edges()
        hosts = [n for n in nodes if 1 == graph.in_degree()[n]+graph.out_degree()[n]]
        for node in nodes:
            if node in hosts:
                self.number_of_host += 1
                h = self.net.addHost("h%d"%self.number_of_host)
                self.nodeMapNet[node] = h
            else:
                self.number_of_switch += 1
                dpid = self.dpid_prefix + "%02d"%self.number_of_switch
                sw = self.net.addSwitch("s%d"%self.number_of_switch, dpid = dpid)
                self.dpid_to_sw[dpid] = sw
                self.nodeMapNet[node] = sw
        if len(hosts) == 0:
            for node in nodes:
                self.net.addHost("h%s" % node)
                self.net.addLink("h%s" % node, node)
        for edge in edges:
            linkopts = dict()
            self.net.addLink(self.nodeMapNet[edge[0]], self.nodeMapNet[edge[1]], **linkopts)
        
    def start(self):
        controllers = []
        for i in range(len(self.c_ip)):
            controller = self.net.addController("c%s"%i, controller=RemoteController, ip=self.c_ip[i])
            controllers.append(controller)
        self.net.build()
        for i, sw in enumerate(self.net.switches):
            c = random.choice(controllers)
            sw.start([c])
        # self.net.waitConnected()
    
    def pingAll(self):
        self.net.pingAll()

    
