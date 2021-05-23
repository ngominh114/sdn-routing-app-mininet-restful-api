import networkx
import random
from mininet.net import Mininet
from mininet.node import RemoteController
import time
def activeIntf(link):
    intf1 = link.intf1
    intf2 = link.intf2
    node1 = intf1.node
    node2 = intf2.node
    print(str(node1), str(intf1))
    if("h" in str(node1)):
        print("AA")
        node2.attach(intf2)
        return
    node1.attach(intf1)
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

    def measure_delay(self):
        netLinks = self.net.links
        h_test1 = self.net.addHost('h_test1')
        h_test2 = self.net.addHost('h_test2')
        link_1 = self.net.addLink('s1', h_test1)
        link_2 = self.net.addLink('s2', h_test2)
        activeIntf(link_1)
        activeIntf(link_2)

        h_test1.setIP('10.0.0.50')
        h_test2.setIP('10.0.0.51')
        # for netLink in netLinks:
        #     intf1 = netLink.intf1
        #     intf2 = netLink.intf2
        #     node1 = intf1.node
        #     node2 = intf2.node
        #     if (("h" in str(node1)) or ("h" in str(node2))):
        #         continue
        #     link_1 = self.net.addLink(node1, h31)
        #     link_2 = self.net.addLink(node2, h32)


        #     time.sleep(1)
        #     # rs = self.net.iperf((h250, h251))

        #     return
        #     # print rs

        #     # self.net.delLink(link_1)
        #     # self.net.delLink(link_2)
