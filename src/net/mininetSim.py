import networkx
import random
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import RemoteController
import time
import re
import os
# def activeIntf(link):
#     intf1 = link.intf1
#     intf2 = link.intf2
#     node1 = intf1.node
#     node2 = intf2.node
#     if("h" in str(node1)):
#         node2.attach(intf2)
#         return
#     node1.attach(intf1)
host_sw = {}
host_sw["h_test1"] = {}
host_sw["h_test2"] = {}

def pingAndParseResult(h1, h2):
    rs = h1.cmd("ping -c2", h2.IP())
    print(rs)
    rs_split = rs.split()
    x = re.findall("\d+\.\d+", rs_split[-2])
    return x
    
class MininetSim():
    def __init__(self):
        self.net = Mininet(topo=None, controller=RemoteController, link=TCLink, build=False)
        self.dpid_to_sw = {}
        self.dpid_prefix = "0000000000000"
        self.nodeMapNet = {}
        self.bw = {}
        self.number_of_switch = 0
        self.number_of_host = 0
        self.c_ip = []
    def generate(self, config):
        node_num = 14

        # Create switches
        for i in range(1, node_num + 1):
            self.net.addSwitch('s%d' %i)

        # Create nodes
        for i in range(1, node_num + 1):
            if i < 10:
                self.net.addHost('h%d' %i, ip = '10.0.0.%d' %i, mac = '00:00:00:00:01:0%d' %i)
            else:
                self.net.addHost('h%d' %i, ip = '10.0.0.%d' %i, mac = '00:00:00:00:01:%d' %i)

        print "*** Creating host-switch links"
        for i in range(1, node_num + 1):
            self.net.addLink('h%d'%i, 's%d' %i, cls=TCLink, bw=20)

        print "*** Creating switch-switch links"
        link_from = [1,2,2,2,2,2,3,3,5,7,8,8,9,9,10,11,12,13]
        link_to = [2,3,4,5,7,8,4,5,6,9,9,12,10,13,11,13,13,14]

        for lf, lt in zip(link_from, link_to):
            self.net.addLink('s%d' % int(lf), 's%d' % int(lt), cls=TCLink, bw=30)
            
        number_of_controllers = len(config["CONTROLLER_IP"])
        for i in range(number_of_controllers):
            self.c_ip.append(config["CONTROLLER_IP"]["ip_%s"%i])
        # filename = config["DIRECTORIES"]["topo"]
        # graph = networkx.read_graphml(filename)
        # nodes = graph.nodes()
        # edges = graph.edges()
        # hosts = [n for n in nodes if 1 == graph.in_degree()[n]+graph.out_degree()[n]]
        # for node in nodes:
        #     if node in hosts:
        #         self.number_of_host += 1
        #         h = self.net.addHost("h%d"%self.number_of_host, ip = '10.0.0.%d'%self.number_of_host,mac = '00:00:00:00:01:%02d' %self.number_of_host)
        #         self.nodeMapNet[node] = h
        #     else:
        #         self.number_of_switch += 1
        #         dpid = self.dpid_prefix + "%03d"%self.number_of_switch
        #         sw = self.net.addSwitch("s%d"%self.number_of_switch, dpid = dpid)
        #         self.dpid_to_sw[dpid] = sw
        #         self.nodeMapNet[node] = sw
        # if len(hosts) == 0:
        #     for node in nodes:
        #         self.net.addHost("h%s" % node)
        #         self.net.addLink("h%s" % node, node)
        # for edge in edges:
        #     bw = random.uniform(3,25)
        #     self.net.addLink(self.nodeMapNet[edge[0]], self.nodeMapNet[edge[1]], bw=bw)
        #     self.bw.setdefault(str(self.nodeMapNet[edge[0]]), {})
        #     self.bw.setdefault(str(self.nodeMapNet[edge[1]]), {})
        #     self.bw[str(self.nodeMapNet[edge[1]])][str(self.nodeMapNet[edge[0]])] = bw
        #     self.bw[str(self.nodeMapNet[edge[0]])][str(self.nodeMapNet[edge[1]])] = bw

        h_test1 = self.net.addHost("h_test1", ip='10.0.0.200')
        h_test2 = self.net.addHost("h_test2", ip='10.0.0.201')

        for sw in self.net.switches:
            link1 = self.net.addLink(sw, h_test1)
            link2 = self.net.addLink(sw, h_test2)
            host_sw[str(h_test1)][str(sw)] = link1
            host_sw[str(h_test2)][str(sw)] = link2
        
    def start(self):
        controllers = []
        for i in range(len(self.c_ip)):
            controller = self.net.addController("c%s"%i, controller=RemoteController, ip=self.c_ip[i])
            controllers.append(controller)
        self.net.build()
        for i, sw in enumerate(self.net.switches):
            c = random.choice(controllers)
            sw.start([c])
        self.net.start()
        h_test1 = self.net.getNodeByName("h_test1")
        h_test2 = self.net.getNodeByName("h_test2")
        self.h_test1_mac = h_test1.MAC()
        self.h_test2_mac = h_test2.MAC()
        self.net.waitConnected()
    
    def pingAll(self):
        self.net.pingAll()

    def prepare(self):
        for sw in self.net.switches:
            self.net.configLinkStatus(str(sw), "h_test1", 'down')
            self.net.configLinkStatus(str(sw), "h_test2", 'down')
            
class TrafficMatrixManager():
    def __init__(self, net):
        self.current_traffic_matrix = {}
        self.latest_traffic_matrix = {}
        self.delay_metrix = {}
        self.current_time = 0
        self.latest_time = 0
        for sw in net.switches:
            self.current_traffic_matrix.setdefault(str(sw), {})
            self.delay_metrix.setdefault(str(sw), {})
            self.latest_traffic_matrix.setdefault(str(sw), {})
    # def create_traffic_data(self, sw1, sw2, net, api):
    #     traffic = self.measure_traffic(sw1, sw2, net, api)
    #     latest_traffic1 = self.get_traffic(sw1, sw2)
    #     latest_traffic1 

    def get_traffic(self, sw1, sw2):
        if not sw2 in self.current_traffic_matrix[sw1]:
            return {}
        return self.current_traffic_matrix[sw1][sw2]
    def measure_traffic(self, sw1, sw2, net, api):
        link = api.getLink(sw1, sw2)
        sw = net.getNodeByName(link["src"]["sw"])
        intf = link["src"]["port"]
        result = sw.dpctl("dump-ports", intf)
        currentTime = time.time()*1000
        result = result.split()
        index = result.index("rx")
        packets_str = result[index+1]
        bytes_str = result[index+2]
        packets = int(re.search(r'\d+', packets_str).group())
        transmit_bytes = int(re.search(r'\d+', bytes_str).group())
        traffic = {"packet":packets, "bytes":transmit_bytes, "time":currentTime}
        print traffic
        return traffic

    def measure_traffic_metrix(self, net):
        matrix = {}
        netLinks = net.links
        for netLink in netLinks:
            intf1 = netLink.intf1
            intf2 = netLink.intf2
            node1 = intf1.node
            node2 = intf2.node
            if (("h" in str(node1)) or (("h" in str(node2)))):
                continue
            currentTime = time.time()*1000
            result1 = node1.dpctl("dump-ports", str(intf1))
            result2 = node2.dpctl("dump-ports", str(intf2))

            result1 = result1.split()
            result2 = result2.split()

            index1 = result1.index("rx")
            index2 = result2.index("rx")

            packets_str1 = result1[index1+1]
            bytes_str1 = result1[index1+2]
            packets_str2 = result2[index2+1]
            bytes_str2 = result2[index2+2]
            packets1 = int(re.search(r'\d+', packets_str1).group())
            transmit_bytes1 = int(re.search(r'\d+', bytes_str1).group())
            packets2 = int(re.search(r'\d+', packets_str2).group())
            transmit_bytes2 = int(re.search(r'\d+', bytes_str2).group())
            traffic1 = {"packet":packets1, "bytes":transmit_bytes1, "time":currentTime}
            traffic2 = {"packet":packets2, "bytes":transmit_bytes2, "time":currentTime}

            node1_str = str(node1)
            node2_str = str(node2)
            if not node1_str in matrix:
                matrix[node1_str] = {}
            matrix[node1_str][node2_str] = traffic1

            if not node2_str in matrix:
                matrix[node2_str] = {}
            matrix[node2_str][node1_str] = traffic2
        self.latest_traffic_matrix = self.current_traffic_matrix
        self.current_traffic_matrix = matrix
        self.latest_time = self.current_time
        self.current_time = time.time()*1000

    def measure_delay(self, sw1, sw2, net, api):
        h_test1 = net.getNodeByName("h_test1")
        h_test2 = net.getNodeByName("h_test2")
        for intf in h_test1.intfList():
            if intf.isUp():
                print(intf.name)
                h_test1.cmd("ifconfig %s down"%str(intf))
        for intf in h_test2.intfList():
            if intf.isUp():
                print(intf.name)
                h_test2.cmd("ifconfig %s down"%str(intf))
        link = api.getLink(sw1, sw2)
        link1 = host_sw["h_test1"][sw1]
        link2 = host_sw["h_test2"][sw2]
        intf1 = link1.intf2
        intf2 = link2.intf2
        net.configLinkStatus(sw1, 'h_test1', 'up')
        net.configLinkStatus(sw2, 'h_test2', 'up')


        h_test1.setIP('10.0.0.200',intf=intf1)
        h_test2.setIP('10.0.0.201',intf=intf2)

        os.system("sudo ovs-ofctl add-flow %s in_port=%s,priority=41000,actions=output:%s"%(sw1, str(link1.intf1), str(link["src"]["port"])))
        os.system("sudo ovs-ofctl add-flow %s in_port=%s,priority=41000,actions=output:%s"%(sw2, str(link["dst"]["port"]), str(link2.intf1)))

        os.system("sudo ovs-ofctl add-flow %s in_port=%s,priority=41000,actions=output:%s"%(sw1, str(link["src"]["port"]), str(link1.intf1)))
        os.system("sudo ovs-ofctl add-flow %s in_port=%s,priority=41000,actions=output:%s"%(sw2, str(link2.intf1), str(link["dst"]["port"])))
        
        x = pingAndParseResult(h_test1, h_test2)
        rs = net.iperf((h_test1,h_test2))
        print(rs)
        os.system("sudo ovs-ofctl del-flows %s --strict priority=41000,in_port=%s"%(sw1, str(link1.intf1)))
        os.system("sudo ovs-ofctl del-flows %s --strict priority=41000,in_port=%s"%(sw2, str(link["dst"]["port"])))

        os.system("sudo ovs-ofctl del-flows %s --strict priority=41000,in_port=%s"%(sw1, str(link["src"]["port"])))
        os.system("sudo ovs-ofctl del-flows %s --strict priority=41000,in_port=%s"%(sw2, str(link2.intf1)))

        return x[-1]
    def measure_delay_metrix(self, net, dataApi):
        for link in net.links:
            intf1 = link.intf1
            intf2 = link.intf2
            sw1 = str(intf1.node)
            sw2 = str(intf2.node)
            if ('h' in sw1 or 'h' in sw2):
                continue
            if not sw1 in self.delay_metrix:
                self.delay_metrix[sw1] = {}
            if not sw2 in self.delay_metrix:
                self.delay_metrix[sw2] = {}
            self.delay_metrix[sw1][sw2] = self.measure_delay(sw1,sw2,net,dataApi)
            self.delay_metrix[sw2][sw1] = self.measure_delay(sw2,sw1,net,dataApi)