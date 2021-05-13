import networkx
import random
import sys
import math
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import MininetLogger
import random
import configparser

config = configparser.ConfigParser()
config._interpolation = configparser.ExtendedInterpolation()
config.read('config.ini')
number_of_controllers = len(config["CONTROLLER_IP"])
c_ip = []
for i in range(number_of_controllers):
    c_ip.append(config["CONTROLLER_IP"]["ip_%s"%i])
filename = config["DIRECTORIES"]["topo"]
graph = networkx.read_graphml(filename)
net = Mininet(topo=None, build=False)
nodes = graph.nodes()
edges = graph.edges()
hosts = [n for n in nodes if 1 == graph.in_degree()[n]+graph.out_degree()[n]]

for node in nodes:
    if node in hosts:
        net.addHost(node)
    else:
        net.addSwitch(node, protocols='OpenFlow13')

if len(hosts) == 0:
    for node in nodes:
        net.addHost("h%s" % node)
        net.addLink("h%s" % node, node)
for edge in edges:
    linkopts = dict()
    net.addLink(edge[0], edge[1], **linkopts)
controllers = []
for i in range(number_of_controllers):
    controller = net.addController("c%s"%i, controller=RemoteController, ip=c_ip[i])
    controllers.append(controller)
net.build()

for i, sw in enumerate(net.switches):
    c = random.choice(controllers)
    sw.start([c])
CLI(net)
net.stop()
