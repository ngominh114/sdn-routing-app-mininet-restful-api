import networkx
import random
from mininet.net import Mininet
from mininet.node import RemoteController
import time
import os
def activeIntf(link):
    intf1 = link.intf1
    intf2 = link.intf2
    node1 = intf1.node
    node2 = intf2.node
    if("h" in str(node1)):
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
        self.host_sw = {}
        self.host_sw["h_test1"] = {}
        self.host_sw["h_test2"] = {}
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

        h_test1 = self.net.addHost("h_test1", ip='10.0.0.200')
        h_test2 = self.net.addHost("h_test2", ip='10.0.0.201')

        for sw in self.net.switches:
            link1 = self.net.addLink(sw, h_test1)
            link2 = self.net.addLink(sw, h_test2)
            self.host_sw[str(h_test1)][str(sw)] = link1
            self.host_sw[str(h_test2)][str(sw)] = link2
        
    def start(self):
        controllers = []
        for i in range(len(self.c_ip)):
            controller = self.net.addController("c%s"%i, controller=RemoteController, ip=self.c_ip[i])
            controllers.append(controller)
        self.net.build()
        for i, sw in enumerate(self.net.switches):
            c = random.choice(controllers)
            sw.start([c])
        self.net.waitConnected()
    
    def pingAll(self):
        self.net.pingAll()

    def prepare(self):
        for sw in self.net.switches:
            self.net.configLinkStatus(str(sw), "h_test1", 'down')
            self.net.configLinkStatus(str(sw), "h_test2", 'down')

    def measure_delay(self, sw1, sw2, api):
        h_test1 = self.net.getNodeByName("h_test1")
        h_test2 = self.net.getNodeByName("h_test2")
        # for intf in h_test1.intfs:
        #     if intf.isUp():
        #         h_test1.cmd("ifconfig %s down"%str(intf))
        # for intf in h_test2.intfs:
        #     if intf.isUp():
        #         h_test2.cmd("ifconfig %s down"%str(intf))
        link = api.getLink(sw1, sw2)
        link1 = self.host_sw["h_test1"][sw1]
        link2 = self.host_sw["h_test2"][sw2]
        intf1 = link1.intf2
        intf2 = link2.intf2
        self.net.configLinkStatus(sw1, 'h_test1', 'up')
        self.net.configLinkStatus(sw2, 'h_test2', 'up')


        h_test1.setIP('10.0.0.200',intf=intf1)
        h_test2.setIP('10.0.0.201',intf=intf2)

        os.system("sudo ovs-ofctl add-flow %s in_port=%s,priority=41000,actions=output:%s"%(sw1, str(link1.intf1), str(link["src"]["port"])))
        os.system("sudo ovs-ofctl add-flow %s in_port=%s,priority=41000,actions=output:%s"%(sw2, str(link["dst"]["port"]), str(link2.intf1)))

        os.system("sudo ovs-ofctl add-flow %s in_port=%s,priority=41000,actions=output:%s"%(sw1, str(link["src"]["port"]), str(link1.intf1)))
        os.system("sudo ovs-ofctl add-flow %s in_port=%s,priority=41000,actions=output:%s"%(sw2, str(link2.intf1), str(link["dst"]["port"])))
        
        rs = h_test1.cmd("ping -c1", h_test2.IP())
        print(rs)
        rs2 = h_test2.cmd("ping -c1", h_test1.IP())
        print(rs)

        os.system("sudo ovs-ofctl del-flows %s --strict priority=41000,in_port=%s"%(sw1, str(link1.intf1)))
        os.system("sudo ovs-ofctl del-flows %s --strict priority=41000,in_port=%s"%(sw2, str(link["dst"]["port"])))

        os.system("sudo ovs-ofctl del-flows %s --strict priority=41000,in_port=%s"%(sw1, str(link["src"]["port"])))
        os.system("sudo ovs-ofctl del-flows %s --strict priority=41000,in_port=%s"%(sw2, str(link2.intf1)))

        # h_test1.stop()
        # h_test2.stop()
            

