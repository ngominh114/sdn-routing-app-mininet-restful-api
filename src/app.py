import networkx
import random
import sys
import os
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

from routing.path.pathCreate import PathCreator
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
dpid = "00000000000000"
hosts = [n for n in nodes if 1 == graph.in_degree()[n]+graph.out_degree()[n]]
number_of_switch = 0
for node in nodes:
    if node in hosts:
        net.addHost(node)
    else:
        number_of_switch = number_of_switch + 1
        net.addSwitch(node, protocols='OpenFlow13', dpid = dpid + "%02d"%number_of_switch)

if len(hosts) == 0:
    for node in nodes:
        net.addHost("h%s" % node)
        net.addLink("h%s" % node, node)
for edge in edges:
    linkopts = dict()
    net.addLink(edge[0], edge[1], **linkopts)

pathCreate = PathCreator()

def findPathAndSetFlow(src, dst):
    srcConnectPoint = api.getConnectPoint(src)
    dstConnectPoint = api.getConnectPoint(dst)
    path = pathCreate.createPath(srcConnectPoint["deviceId"], dstConnectPoint["deviceId"])
    print(path)
app = Flask(__name__)
@app.route('/pingAll', methods = ['GET'])
def pingAll():
    n8 = net.getNodeByName('n8')
    n9 = net.getNodeByName('n9')
    net.ping([n8, n9])
    return ""
@app.route('/cancel', methods=['GET'])
def cancel():
    os.system("")
@app.route('/', methods=['GET'])
def start():
    controllers = []
    for i in range(number_of_controllers):
        controller = net.addController("c%s"%i, controller=RemoteController, ip=c_ip[i])
        controllers.append(controller)
    net.build()
    for i, sw in enumerate(net.switches):
        c = random.choice(controllers)
        sw.start([c])
    return ""
@app.route('/setFlow', methods = ["POST"])
def setFlow():
    data = request.get_json()
    src = data["src"]
    dst = data["dst"]
    findPathAndSetFlow(src, dst)
    return ""
@app.route('/shutdown', methods = ['GET'])
def bye():
    net.stop()
    os.system("sudo mn -c")
    return ""

@app.route('/devices.store', methods = ['POST'])
def updateDevices():
    data = request.get_json()
    api.updateDevice(data)
    pathCreate.graph.updateGraph(api.data)
    return ""


@app.route('/hosts.store', methods = ['POST'])
def updateHosts():
    data = request.get_json()
    api.updateHost(data)
    return ""

@app.route('/links.store', methods = ['POST'])
def updateLinks():
    data = request.get_json()
    api.updateLink(data)
    pathCreate.graph.updateGraph(api.data)
    return ""
