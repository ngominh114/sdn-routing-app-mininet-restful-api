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
from data.dataAPI import DataAPI
from flask import Flask
from flask import request
import json


api = DataAPI()
api.read()
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

def getSwitch(id):
    for sw in net.switches:
        print(sw.dpid)
        print(id)

app = Flask(__name__)
@app.route('/pingAll', methods = ['GET'])
def pingAll():
    net.pingAll()
    return ""

@app.route('/', methods=['GET'])
def start():
    controllers = []
    for i in range(number_of_controllers):
        controller = net.addController("c%s"%i, controller=RemoteController, ip=c_ip[i])
        controllers.append(controller)
    net.build()
    for i, sw in enumerate(net.switches):
        c = random.choice(controllers)
        print(i)
        sw.start([c])
    return ""

@app.route('/shutdown', methods = ['GET'])
def bye():
    net.stop()
    return ""

@app.route('/devices.store', methods = ['POST'])
def addDevices():
    # print(request.args)
    # print(data)
    # api.updateDevice(devices)
    return ""


@app.route('/flows.store', methods = ['POST'])
def addFlows():
    data = request.get_json()
    getSwitch(1)
    print(data['1'])
    return ""

