import networkx
import random
import os
from mininet.net import Mininet
from mininet.node import RemoteController
import random
import configparser
from data.dataAPI import DataAPI
from flask import Flask
from flask import request
from routing.flow import setter
from mininet.cli import CLI
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
dpid_prefix = "00000000000000"
hosts = [n for n in nodes if 1 == graph.in_degree()[n]+graph.out_degree()[n]]
number_of_switch = 0
number_of_host = 0
nodeMapNet = {}
for node in nodes:
    if node in hosts:
        number_of_host += 1
        h = net.addHost("h%d"%number_of_host)
        nodeMapNet[node] = h
    else:
        number_of_switch = number_of_switch + 1
        dpid = dpid_prefix + "%02d"%number_of_switch
        sw = net.addSwitch("s%d"%number_of_switch, dpid = dpid)
        nodeMapNet[node] = sw
if len(hosts) == 0:
    for node in nodes:
        net.addHost("h%s" % node)
        net.addLink("h%s" % node, node)
for edge in edges:
    linkopts = dict()
    net.addLink(nodeMapNet[edge[0]], nodeMapNet[edge[1]], **linkopts)

pathCreate = PathCreator()
links ={}
def findPathAndSetFlow(src, dst):
    srcHost = api.getHostByMac(str.lower(str(src)))
    dstHost = api.getHostByMac(str.lower(str(dst)))
    if (srcHost == None or dstHost == None):
        return
    path = pathCreate.createPath(srcHost["connectPoint"]["sw"], dstHost["connectPoint"]["sw"])
    print(path)
    setter.installFlow(path, srcHost, dstHost)
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
        sw.start([c])
    net.waitConnected()
    return ""
@app.route('/setFlow', methods = ["POST"])
def setFlow():
    data = request.get_json()
    src = data["src"]
    dst = data["dst"]
    findPathAndSetFlow(src, dst)
    return ""

@app.route('/data.store', methods = ['GET'])
def updateData():
    api.updateDataByNet(net)
    pathCreate.graph.updateGraph(api.data)
    return ""

@app.route('/findPath', methods=["GET"])
def findPath():
    h1 = net.getNodeByName("h1")
    h5 = net.getNodeByName("h5")
    h1.cmd("ping -c1 " + str(h5.IP()))
    return ""
# @app.route('/hosts.store', methods = ['GET'])
# def updateHosts():
#     # data = request.get_json()
#     api.buildHostDataByNet(net)
#     return ""

# @app.route('/links.store', methods = ['POST'])
# def updateLinks():
#     data = request.get_json()
#     api.updateLink(data)
#     pathCreate.graph.updateGraph(api.data)
#     return ""
